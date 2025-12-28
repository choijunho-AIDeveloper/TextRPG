"""Model Download Script"""

import os
import argparse
from transformers import AutoModelForCausalLM, AutoTokenizer


def download_model(model_name: str, save_directory: str = "./models"):
    """
    Download model and tokenizer to local directory
    """
    print("=" * 80)
    print(f"모델 다운로드 시작: {model_name}")
    print("=" * 80)

    # Create directory if it doesn't exist
    os.makedirs(save_directory, exist_ok=True)

    # Download tokenizer
    print("\n" + '토크나이저 다운로드 시작...')
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True
    )
    tokenizer.save_pretrained(save_directory)
    print("\n" + '토크나이저 다운로드 완료')

    # Download model
    print('모델 다운로드 시작...')
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype="auto"
    )
    model.save_pretrained(save_directory)
    print('모델 다운로드 완료')

    print("\n" + "=" * 80)
    print("모든 다운로드가 완료되었습니다!")
    print(f"모델 저장 위치: {os.path.abspath(save_directory)}")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Default 모델을 로컬에 다운로드합니다.")
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen3-4B-Instruct-2507",
        help="다운로드할 모델 이름: Qwen/Qwen3-4B-Instruct-2507"
    )
    parser.add_argument(
        "--save-dir",
        type=str,
        default="./models/Qwen/Qwen3-4B-Instruct-2507",
        help="기본값: ./models/Qwen/Qwen3-4B-Instruct-2507"
    )

    args = parser.parse_args()

    try:
        download_model(args.model, args.save_dir)
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
