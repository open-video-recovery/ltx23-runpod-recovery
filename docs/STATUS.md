# LTX 2.3 / 10Eros v1.4 — 技術的な確認結果

更新：2026-11-06

## 公開GHCR版

```text
ghcr.io/open-video-recovery/ltx23-10eros-licensed@sha256:cb6dc2a1dac7945f154c3ed48bd3493d921fe3bbb430a251db954f6596780082
```

- GHCRのOCIマニフェストを固定Digestで照合し、**匿名Pull成功**。
- 原モデル・Worker・Workflowを含む既存の22 OCIレイヤーをそのまま使用。
- 追加したライセンス／NOTICEのレイヤーとメタデータを更新。LTX、Gemma、ComfyUI、Gemma NOTICE、LTX AUP、Gemma禁止事項を収録。
- 初期リリースの圧縮OCIのうち、モデル用の特大レイヤーは転送可能な小さいレイヤーに分割され、起動時に元データへ復元されます。

## RunPodでの検証（2026-11-05）

- 24GB GPU（ADA_24）×1、Container Disk 150GB、Min Workers 0／Max Workers 1。
- 640×960・24fps・約5秒の動画生成ジョブが **COMPLETED**。
- 329,525バイトのMP4を取得。後続のCPU検証で、H.264・121フレーム・5.041667秒をFFprobeで確認し、FFmpegで全フレームを正常デコード。
- 初回ジョブの完了まで約12分。大容量イメージの取得・展開時間を含むため、環境により変わります。
- 検証専用Endpointはテスト終了後に削除し、既存Endpoint11件がそのまま残っていることを確認しました。

最新のGHCR版ではNOTICEとOCIの説明用メタデータだけを変更しており、上記GPUで動作したモデル・Worker・Workflow用レイヤーは同じバイト列です。**更新後Digestでの追加GPUテストは行っていません。** 映像の主観的な品質・セリフ・音声内容はこの技術検証の対象外です。

## 利用規約

上流の利用条件は [NOTICE-THIRD-PARTY.md](../NOTICE-THIRD-PARTY.md) を参照してください。OCIに規約・NOTICEを同梱しています。元の著作者と本再パッケージ提供者は別主体です。
