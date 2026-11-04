# 匿名公開プロジェクトの運用手順

このプロジェクトは初期研究版で、RunPodでのGPU動画生成はまだ確認していません。
本物の旧 `workflows/i2v.json` も収録していません。

## 開発者による確認
- GitHub Actions `Recovery kit CPU checks` が成功していること。
- `models.lock.json` のrevisionとSHA256を維持すること。
- モデル重み、秘密鍵、APIキー、私有データを公開しないこと。
- 第三者の元PythonやWorkflowの配布許諾を確認すること。
- GPUでMP4と生成ログを確認する前に「復旧完了」と宣伝しないこと。

## 利用者向けのCPU環境チェック

```bash
python3 -m unittest discover -s tests -v
python3 -m pip install 'huggingface_hub>=0.30,<2'
python3 scripts/download_models.py --model-root /path/to/ComfyUI/models
python3 scripts/verify_models.py --model-root /path/to/ComfyUI/models
```

上記のモデルダウンロードには大容量ディスクと回線が必要です。モデルを取得するだけでは動画は生成できません。

## リリースまでに不足しているもの

1. 旧Workflowの合法的な復元、または公開情報に基づく独立Workflowの作成とGPU検証。
2. ComfyUI / custom node / PyTorch-CUDAのバージョン固定。
3. Dockerイメージビルド、RunPod GPU上で画像からMP4生成、ジョブIDと費用を記録。
4. 画像ダイジェストと出力を検証し、初めて安定版を発行。
