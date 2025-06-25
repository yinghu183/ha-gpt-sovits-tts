# Home Assistant 的 GPT-SoVITS TTS 集成

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/)

## **本项目所有代码包括说明文件均使用gemini-2.5-pro完成，发布者仅负责提出要求和贴出BUG日志。**

这是一个为 Home Assistant 开发的自定义文本转语音（TTS）集成。它允许您连接到自己部署的 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) 服务，使用您自己训练的音色模型在智能家居中进行语音播报。

## ✨ 功能特性

- **完全本地化**：所有语音合成都在您自己的服务器上完成，无需依赖云服务，保护隐私。
- **高度定制化**：使用您通过 GPT-SoVITS 训练的任何声音作为播报音色。
- **配置简单**：通过 `configuration.yaml` 文件即可快速配置和使用。
- **无缝集成**：作为标准的 TTS 平台集成到 Home Assistant 中，可以在自动化、脚本中方便地调用。

## ⚙️ 先决条件

在安装此集成之前，请确保您已具备：

1.  一个正在运行的 Home Assistant 实例。
2.  一个已经成功部署并正在运行的 GPT-SoVITS 服务，并且您的 Home Assistant 服务器可以访问到它。

## 🚀 安装

### 方法一：通过 HACS (推荐)

HACS (Home Assistant Community Store) 是安装自定义集成的首选方法。

1.  打开您的 Home Assistant，进入 **HACS** > **集成**。
2.  点击右上角的三个点，选择 **自定义存储库**。
3.  在弹出的对话框中，填入此项目的 GitHub 仓库地址：
    ```
    https://github.com/yinghu183/ha-gpt-sovits-tts
    ```
4.  在 **类别** 栏，选择 **集成 (Integration)**。
5.  点击 **添加 (ADD)**。
6.  关闭自定义存储库对话框后，您应该能在 HACS 集成列表中找到 "GPT-SoVITS TTS"。点击 **下载 (DOWNLOAD)**。
7.  下载完成后，按照提示**重启 Home Assistant**。

### 方法二：手动安装

1.  在此项目的 GitHub 页面，下载最新的代码。
2.  解压后，找到 `custom_components` 文件夹下的 `gpt_sovits` 目录。
3.  将整个 `gpt_sovits` 目录复制到您 Home Assistant 配置目录下的 `custom_components` 文件夹中。
    *   最终的路径看起来应该是：`<ha_config_dir>/custom_components/gpt_sovits/`
4.  **重启 Home Assistant**。

## 📝 配置

安装完成后，您需要在 `configuration.yaml` 文件中添加此集成的配置。

```yaml
# configuration.yaml 示例
tts:
  - platform: gpt_sovits
    # --- 必填项 ---
    host: "192.168.xxx.xxx"  # 您的 GPT-SoVITS 服务器的 IP 地址
    port: xxxx              # GPT-SoVITS 服务的端口号，默认为 9880
    refer_wav_path: "/workspace/GPT-SoVITS/output/slicer_opt/your_audio.wav" # 重要：这是位于GPT-SoVITS服务器上的参考音频的绝对路径，不是Home Assistant服务器上的路径
    prompt_text: "这是参考音频对应的文本内容。" # 与参考音频内容匹配的文本
    
    # --- 可选项 (不填则使用默认值) ---
    prompt_language: "zh"   # 参考文本的语言 (zh, en, ja)，默认为 "zh"
    text_language: "zh"     # 要合成的文本的语言 (zh, en, ja)
    speed: 1.0              # 语速，默认为 1.0
    temperature: 1.0        # 温度参数，影响声音的随机性，默认为 1.0
```
**配置说明:**

- `host`: 运行 GPT-SoVITS 服务的服务器IP。
- `refer_wav_path`: **这是最关键的配置**。它必须是 **GPT-SoVITS 服务器上**参考音频的**绝对路径**。集成会把这个路径原封不动地发送给 GPT-SoVITS API。
- `prompt_text`: 与参考音频内容完全匹配的文本，帮助模型更好地进行音色克隆。

完成配置后，请再次**重启 Home Assistant** 以加载您的配置。

## 🗣️ 如何使用

配置并重启后，Home Assistant 中会自动创建一个名为 `tts.gpt_sovits_say` 的服务。

您可以在 **开发者工具** > **动作** 中测试它，或在您的自动化和脚本中调用。

### 服务调用示例 (YAML)

```yaml
service: tts.gpt_sovits_say
target:
  entity_id: media_player.your_speaker_entity # 替换成您的播放器实体ID
data:
  message: "你好，世界！这是来自家庭助理的测试语音。"
  language: "zh" # 可选，指定本次播报的语言
  options:
    speed: 1.2 # 可选，临时覆盖默认语速
```
## ❓ 常见问题

**Q: 调用服务后，音箱没有声音，日志里出现超时错误。**
**A:** GPT-SoVITS 生成音频需要一定时间，特别是长文本。本集成内置了较长的超时时间（300秒）。如果仍然超时，请检查您的 GPT-SoVITS 服务器是否性能不足，或者网络连接是否稳定。

**Q: 我可以有多个音色吗？**
**A:** 当前版本（v1.0.0）通过 `configuration.yaml` 只能配置一个固定的音色。未来的版本计划支持 UI 配置和动态选择音色。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📄 开源许可

本项目基于 [MIT License](LICENSE) 开源。
