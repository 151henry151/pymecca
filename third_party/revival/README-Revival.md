# MeccanoidRevival

> A community-driven open-source project to bring the **Meccanoid** robots back to life — firmware, protocol, and control app included.

---

## 🔧 Mission

The **Meccanoid** robots by **Meccano / Spin Master** were innovative and full of potential, but their software ecosystem has been deprecated and the original companion apps are no longer functional.  
**MeccanoidRevival** aims to **restore full control** of these robots through open-source development, documentation, and reverse engineering.

We aim to:
- Decode the **Bluetooth LE communication protocol** used by Meccanoid.
- Build a **new cross-platform control app** (desktop, Android, or web-based).
- Provide, when legally possible, an **open-source APK** or build instructions for a fully **offline/local control app**.
- Develop an **open firmware interface** for motion, speech, and servo control.
- Enable **custom behaviors, programmable sequences, and AI-assisted interactions**.
- Preserve and modernize these robots so they remain usable and hackable.

---

## 🔍 Reverse Engineering and Local Control

Our goal is to make Meccanoid **fully controllable offline**, without any dependence on deprecated servers or online authentication.

This includes:
- Reverse engineering the **original Android app** to understand BLE handshake and command structure.
- Documenting all communication sequences and mapping the control protocol.
- Developing an **open-source replacement app** capable of local control over Bluetooth.
- Providing detailed **build instructions** and tooling for users to build their own APK legally and safely.

> ⚠️ **Legal note:**  
> We will not distribute proprietary code, assets, or copyrighted binaries.  
> All work is for educational and interoperability purposes under fair use.

---

## 🧠 Project Scope

| Area | Goal | Tools / Skills |
|------|------|----------------|
| BLE Protocol Reverse Engineering | Sniff and document Meccanoid BLE commands | nRF Sniffer, Wireshark, Python BLE libraries |
| Firmware Interaction | Open control over motion, LEDs, and servos | Arduino / STM32 / CircuitPython |
| Offline App | Build a new cross-platform app (offline, open-source) | Android (Kotlin), Flutter, React Native |
| Documentation | Create detailed specs, protocol maps, and guides | Markdown, GitHub Wiki |
| Community | Organize collaboration and issues | Discord / Matrix / GitHub Issues |

---

## 🧩 Current Status

| Component | Status | Notes |
|------------|--------|-------|
| BLE Packet Capture | 🟡 In Progress | Partial command mapping known |
| Servo Control | 🔴 Not Functional Yet | Protocol documentation needed |
| Offline App / APK | 🟡 Concept Stage | Seeking Android/Flutter developers |
| Firmware Hooks | 🟡 Researching | Possible microcontroller interface |
| Documentation | 🟢 Started | Protocol snippets being logged |

---

## 🤝 How to Contribute

We are looking for:
- **Android / Flutter developers** to build an offline control app (APK).
- **Reverse engineers** with BLE or serial protocol expertise.
- **Firmware developers** for servo and MCU interfacing.
- **DevOps engineers** for automated APK builds and signing.
- **Documentation writers** for clear, structured protocol specs.

### Get started:
1. Fork this repository  
2. Check or open [Issues](https://github.com/MeccanoidRevival/MeccanoidRevival/issues)  
3. Share BLE packet logs or APK analysis results  
4. Submit Pull Requests or prototypes  

---

## 🧾 Legal Disclaimer

This is a **non-commercial, community-led** project.  
We are **not affiliated with Meccano® or Spin Master™**.  
All reverse engineering, firmware work, and app development are conducted **for research, interoperability, and preservation purposes**.

---

## 🌍 Resources

- [Official Meccanoid Info (archived)](https://web.archive.org/web/*/https://www.meccano.com/meccanoid)
- [About Meccanoid (archived)](https://web.archive.org/web/20151025002525/http://www.meccano.com/meccanoid-about/)
- [Original Meccanoid Site (archived)](https://web.archive.org/web/20210529221708/http://www.meccano.com/)
- [Meccanoid Commercials (archived)](https://web.archive.org/web/20151031062918/http://www.meccano.com/videos)
- [Meccabrain Teardown/Surgery](https://umplesplace.wordpress.com/2016/10/16/meccanoid-g15-brain-surgery/)
- [Neil Fraser’s Meccanoid Firmware Notes](https://neil.fraser.name/news/2021/09/13/)  
- [Python Meccanoid Reverse Engineering Repo](https://github.com/iamsrp/pymecca)

---

## 💬 Contact and Community

- Discord / Matrix Server: Coming soon  
- Email: **meccanoid.revival@tiscali.it**

---

### ⚡ Vision

We believe open-source robotics keeps technology **alive beyond corporate lifecycles**.  
By reviving Meccanoid, we bridge **nostalgia and innovation** — giving a second life to an extraordinary piece of hardware.

> “When a platform dies, open source keeps it breathing.”

---

*Maintained by the MeccanoidRevival Community.*
