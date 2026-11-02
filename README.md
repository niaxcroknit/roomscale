# 룸 스케일

잰 치수 그대로 방에 가구를 놓아 보고, 옷장 속 리빙박스까지 미리 맞춰 보는 안드로이드 앱이에요.

- 패키지 이름: `com.nia.roomscale`
- 기준 버전: Android 16 (API 36), 최소 Android 7.0
- 개인정보처리방침: https://app.notion.com/p/4064235ad3ee8015b12ee4da0bf19985?source=copy_link
- 문의: kimseohappiness@gmail.com

## 안내서

1. **[시작하기.md](시작하기.md)** — Android Studio로 열기, 폰에서 실행, 출시 파일(.aab) 만들기
2. **[PLAY_STORE.md](PLAY_STORE.md)** — 구글 플레이 콘솔 등록부터 정식 출시까지
3. **[store/](store)** — 스토어에 올릴 아이콘, 그래픽 이미지, 스크린샷, 문구

## Android Studio에서 열기

Node 설치 없이 바로 열려요.

- **처음 받을 때:** Android Studio 첫 화면 → **Clone Repository**(또는 Get from VCS) → `https://github.com/niaxcroknit/roomscale` → Clone.
  열린 뒤 왼쪽 프로젝트 창에서 `android` 폴더를 **File → Open**으로 다시 열어요.
  (또는 이 페이지 위 초록색 **Code → Download ZIP**으로 받아 압축을 풀고 `android` 폴더를 열어도 돼요)
- `android` 폴더는 옆의 `node_modules` 폴더를 같이 쓰기 때문에, `android` 폴더만 따로 빼서 옮기면 안 돼요.

## 자동 빌드 (GitHub Actions)

`main`에 코드를 올릴 때마다 GitHub가 앱을 대신 빌드해 봐요. 위쪽 **Actions** 탭에서 결과를 볼 수 있어요.

- 초록 체크 ✅: 빌드 성공. 실행 기록을 눌러 맨 아래 **Artifacts**에서 받을 수 있어요.
  - `roomscale-debug-apk` — 폰에 바로 깔아 보는 테스트용 APK
  - `roomscale-release-aab` — 출시용 AAB (서명 키를 넣어 두지 않았다면 서명이 안 돼 있어서, 플레이에는 Android Studio에서 만든 aab를 올려요)
- 빨간 X ❌: 빌드가 깨졌다는 뜻이에요. Claude에게 알려 주세요.

플레이에 올릴 aab까지 GitHub에서 만들고 싶으면 `.github/workflows/android-build.yml` 맨 위 설명대로 서명 키를 Secrets에 넣으면 돼요.

## 폴더 구조

```
android/        Android Studio로 여는 폴더 (앱 본체)
www/            앱 화면 (HTML) — android 안에 복사돼 있어요
web-source/     원본 웹 페이지 (Claude에서 만든 것)
store/          스토어 등록 이미지·문구·개인정보처리방침
tools/          화면·아이콘·스토어 이미지를 다시 만드는 스크립트
node_modules/   안드로이드 빌드에 필요한 Capacitor 부품 4개
```
