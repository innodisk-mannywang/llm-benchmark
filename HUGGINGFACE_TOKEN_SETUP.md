# HuggingFace Token 設置說明

## 問題描述
在執行 `run-vllm-gptoss.sh` 時遇到 401 Unauthorized 錯誤，這是因為缺少有效的 HuggingFace Token 來訪問某些模型。

## 解決方案

### 方法 1：設置環境變量（推薦）
```bash
export HUGGING_FACE_HUB_TOKEN="your_huggingface_token_here"
./run-vllm-gptoss.sh --no-pull
```

### 方法 2：在運行時指定 Token
```bash
HUGGING_FACE_HUB_TOKEN="your_huggingface_token_here" ./run-vllm-gptoss.sh --no-pull
```

### 方法 3：使用腳本參數
```bash
./run-vllm-gptoss.sh --hf_token "your_huggingface_token_here" --no-pull
```

## 獲取 HuggingFace Token

1. 訪問 [HuggingFace Settings](https://huggingface.co/settings/tokens)
2. 登入您的 HuggingFace 帳戶
3. 點擊 "New token"
4. 選擇 "Read" 權限（對於公開模型）
5. 複製生成的 token

## 使用公開模型（無需 Token）

如果您想使用不需要特殊權限的公開模型，可以指定其他模型：

```bash
./run-vllm-gptoss.sh --model_name "microsoft/DialoGPT-medium" --no-pull
```

## 安全注意事項

- 不要將 HuggingFace Token 硬編碼在腳本中
- 使用環境變量來管理敏感信息
- 定期輪換您的 Token
- 不要在公開的 Git 倉庫中提交包含 Token 的代碼
