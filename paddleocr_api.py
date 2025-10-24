import base64
from io import BytesIO
import os
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import uvicorn
import requests
import time
import json
import gc
import traceback

LOCAL_PATH = "/root/paddleocr-vl/models/PaddleOCR-VL"  # 修改为实际路径

print(f"=== PaddleOCR-VL API 启动中 ===")
print(f"模型路径: {LOCAL_PATH}")

try:
    processor = AutoProcessor.from_pretrained(LOCAL_PATH, trust_remote_code=True, use_fast=True)
    
    # 尝试加载float16，失败则回退到float32
    try:
        print("尝试加载 float16 模型...")
        model = AutoModelForCausalLM.from_pretrained(
            LOCAL_PATH, 
            trust_remote_code=True, 
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True
        ).to("cpu")
        print("使用 float16 精度")
    except Exception as e:
        print(f"float16 加载失败，回退到 float32: {e}")
        model = AutoModelForCausalLM.from_pretrained(
            LOCAL_PATH, 
            trust_remote_code=True, 
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        ).to("cpu")
        print("使用 float32 精度")
    
    model.eval()
    model.generation_config.pad_token_id = model.config.pad_token_id
    print("模型加载成功")
except Exception as e:
    print(f"模型加载失败: {e}")
    traceback.print_exc()
    raise

app = FastAPI()

@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "paddleocr-vl",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "custom",
                "permission": [],
                "root": "paddleocr-vl",
                "parent": None,
                "capabilities": {
                    "vision": True,
                    "function_calling": False,
                    "fine_tuning": False
                }
            }
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(body: dict):
    try:
        messages = body.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="请求体中缺少messages字段")

        content = messages[-1].get("content", [])
        if isinstance(content, str):
            text_prompt = content
            image_urls = []
        else:
            text_parts = [c["text"] for c in content if c["type"] == "text"]
            text_prompt = " ".join(text_parts) or "Parse the document."
            image_urls = [c["image_url"]["url"] for c in content if c["type"] == "image_url"]
    except KeyError as e:
        print(f"请求格式错误: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"请求格式错误: {e}")

    images = []
    for idx, url in enumerate(image_urls):
        img = None
        try:
            if url.startswith("data:"):
                if "," in url:
                    _, b64_data = url.split(",", 1)
                elif url.startswith("data:image/"):
                    b64_data = url.replace("data:image/", "").split(";")[0]
                else:
                    b64_data = url.replace("data:", "")
                
                img_bytes = base64.b64decode(b64_data)
                img = Image.open(BytesIO(img_bytes))
            else:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
        except requests.exceptions.RequestException as e:
            print(f"图片下载失败: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=400, detail=f"图片下载失败: {e}")
        except Exception as e:
            print(f"图片处理失败: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=400, detail=f"图片处理失败: {e}")

        if img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)

    image = images[0] if images else None

    chat_messages = [{"role": "user", "content": text_prompt}]
    
    try:
        prompt = processor.tokenizer.apply_chat_template(
            chat_messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
    except Exception as e:
        print(f"Chat template 失败，使用备用格式: {e}")
        cls_token = "<|begin_of_sentence|>"
        if image:
            prompt = f"{cls_token}User: <|IMAGE_START|><|IMAGE_PLACEHOLDER|><|IMAGE_END|>{text_prompt}\nAssistant: "
        else:
            prompt = f"{cls_token}User: {text_prompt}\nAssistant: "

    try:
        inputs = processor(text=prompt, images=image, return_tensors="pt").to("cpu")
        
        # processor处理完成后，立即关闭图片释放内存
        for img in images:
            try:
                img.close()
            except:
                pass
    except Exception as e:
        print(f"输入处理失败: {e}")
        traceback.print_exc()
        # 发生异常时也要清理图片
        for img in images:
            try:
                img.close()
            except:
                pass
        raise HTTPException(status_code=500, detail=f"输入处理失败: {e}")

    try:
        max_tokens = body.get("max_tokens", 131072)
        temperature = body.get("temperature", 0.7)
        
        print(f"开始推理 (max_tokens={max_tokens}, temp={temperature})...")
        with torch.no_grad():
            outputs = model.generate(
                **inputs, 
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                use_cache=True,
                pad_token_id=processor.tokenizer.pad_token_id,
                eos_token_id=processor.tokenizer.eos_token_id,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                top_p=0.9,
                top_k=50
            )
        print("推理完成")
    except Exception as e:
        print(f"模型推理失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"模型推理失败: {e}")
    
    full_output = processor.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # 保存token计数用于usage统计
    prompt_tokens = len(inputs["input_ids"][0])
    total_tokens = len(outputs[0])
    completion_tokens = total_tokens - prompt_tokens
    
    # 清理推理内存
    del inputs
    del outputs
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()
    
    if "Assistant: " in full_output:
        parts = full_output.split("Assistant: ")
        generated = parts[-1].strip() if len(parts) > 1 else full_output
    else:
        generated = full_output.replace(prompt, "").strip()

    stream = body.get("stream", False)
    completion_id = f"chatcmpl-{int(time.time())}"
    created_time = int(time.time())
    
    # 清理图片内存
    if image:
        del image
    if images:
        del images
    
    if stream:
        async def generate_stream():
            words = generated.split()
            chunk_size = 3
            
            for i in range(0, len(words), chunk_size):
                chunk_text = " ".join(words[i:i+chunk_size])
                if i + chunk_size < len(words):
                    chunk_text += " "
                
                chunk = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created_time,
                    "model": "paddleocr-vl-0.9b",
                    "choices": [{
                        "index": 0,
                        "delta": {
                            "role": "assistant" if i == 0 else None,
                            "content": chunk_text
                        },
                        "finish_reason": None
                    }]
                }
                
                if chunk["choices"][0]["delta"]["role"] is None:
                    del chunk["choices"][0]["delta"]["role"]
                
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
            
            final_chunk = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created_time,
                "model": "paddleocr-vl-0.9b",
                "choices": [{
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }]
            }
            yield f"data: {json.dumps(final_chunk, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(generate_stream(), media_type="text/event-stream")
    
    else:
        response = {
            "id": completion_id,
            "object": "chat.completion",
            "created": created_time,
            "model": "paddleocr-vl-0.9b",
            "choices": [{
                "index": 0, 
                "message": {
                    "role": "assistant", 
                    "content": generated
                }, 
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": prompt_tokens, 
                "completion_tokens": completion_tokens, 
                "total_tokens": total_tokens
            }
        }
        
        return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7777)