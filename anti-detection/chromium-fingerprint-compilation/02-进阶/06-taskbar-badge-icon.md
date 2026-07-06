
一、目标：
-----

*   目标一：传入参数`--notice-number=899`，可以在chromium的任务栏图标上，覆盖一个对应数字的提示。

图形展示如下：

![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/32c687e6dc20461db8a317e043b8ad4b.png) ![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/0af52b5807a24458a3569b44f183337e.png)

> 阅读此篇博客前，请确保已具备chromium编译基础。

二、为什么要给任务栏加提示图标：
----------------

*   1.指纹浏览器多开后，数量太多，需要使用不同的图标来区分不同的浏览器进程。
*   2.类似重要信息，可以用来作为重要信息的提示，比较醒目。

三、修改chromium源码：
---------------

*   打开：`/chrome/browser/win/app_icon.cc`

##### 1.加入头部引用：

```c
#include <iostream>
#include <Shobjidl.h>
#include <windows.h>
#include <shellapi.h>
#include "base/command_line.h"
#include "ui/aura/window_tree_host.h"
```

##### 2\. 新增插入3个函数：

*   新增函数1：生成带数字的ico图片：

```c
HICON CreateNumberIcon(int number, int width) {
    if (number > 999) number = 999;

    // 创建32位ARGB位图
    HDC hdcScreen = GetDC(nullptr);
    HDC hdcMem = CreateCompatibleDC(hdcScreen);
    
    BITMAPINFO bmi = { sizeof(BITMAPINFOHEADER) };
    bmi.bmiHeader.biWidth = width;
    bmi.bmiHeader.biHeight = -width; // 自上而下
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = 32; // 关键：32位带Alpha通道
    bmi.bmiHeader.biCompression = BI_RGB;

    void* pBits = nullptr;
    HBITMAP hBitmap = CreateDIBSection(hdcMem, &bmi, DIB_RGB_COLORS, &pBits, nullptr, 0);
    HBITMAP hOldBitmap = static_cast<HBITMAP>(SelectObject(hdcMem, hBitmap));

    // ==== 关键修改1：初始化透明背景 ====
    memset(pBits, 0, width * width * 4); // 所有像素设为RGBA(0,0,0,0)

    // 绘制红色圆形（保留透明区域）
    HBRUSH hBrush = CreateSolidBrush(RGB(200, 60, 10)); //红色背景
    //HBRUSH hBrush = CreateSolidBrush(RGB(255, 69, 0));
    HBRUSH hOldBrush = static_cast<HBRUSH>(SelectObject(hdcMem, hBrush));
    Ellipse(hdcMem, 0, 0, width, width);
    SelectObject(hdcMem, hOldBrush);
    DeleteObject(hBrush);

    // 设置文字属性
    int fontSize = (number > 99) ? width/1.8 : width/1.3;
    LOGFONT lf = { fontSize, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE, DEFAULT_CHARSET };
    wcscpy_s(lf.lfFaceName, L"Arial");
    HFONT hFont = CreateFontIndirect(&lf);
    HFONT hOldFont = static_cast<HFONT>(SelectObject(hdcMem, hFont));
    
    SetTextColor(hdcMem, RGB(254, 254, 251)); // 文字颜色
    SetBkMode(hdcMem, TRANSPARENT);            // 文字背景透明

    // 绘制居中文字
    std::wstring text = std::to_wstring(number);
    RECT rect = { 0, 0, width, width };
    DrawText(hdcMem, text.c_str(), -1, &rect, DT_CENTER | DT_VCENTER | DT_SINGLELINE);

    // ==== 关键修改2：设置Alpha通道 ====
    DWORD* pixels = static_cast<DWORD*>(pBits);
    const int totalPixels = width * width;
    for (int i = 0; i < totalPixels; ++i) {
        if (pixels[i] & 0x00FFFFFF) { // RGB通道非黑色
            pixels[i] |= 0xFF000000;  // 设置Alpha=255
        }
    }

    // 清理资源
    SelectObject(hdcMem, hOldFont);
    DeleteObject(hFont);
    SelectObject(hdcMem, hOldBitmap);
    DeleteDC(hdcMem);
    ReleaseDC(nullptr, hdcScreen);

    // 创建图标
    ICONINFO iconInfo = { TRUE, 0, 0, hBitmap, hBitmap };
    HICON hIcon = CreateIconIndirect(&iconInfo);
    DeleteObject(hBitmap);

    return hIcon;
}
```

> 这个函数可以生成一个红底白字，透明背景的ico图片。

*   新增函数2：将ico覆盖到另一个ico上：

```c

HICON CombineIconWithBadge(HICON hOriginalIcon, HICON num) {
  // 获取原始图标尺寸
  ICONINFO originalInfo = {0};
  GetIconInfo(hOriginalIcon, &originalInfo);
  BITMAP originalBmp = {0};
  GetObject(originalInfo.hbmColor, sizeof(BITMAP), &originalBmp);
  const int baseWidth = originalBmp.bmWidth;
  const int baseHeight = originalBmp.bmHeight;
  
  // 获取徽章图标尺寸
  ICONINFO badgeInfo = {0};
  GetIconInfo(num, &badgeInfo);
  BITMAP badgeBmp = {0};
  GetObject(badgeInfo.hbmColor, sizeof(BITMAP), &badgeBmp);
  const int badgeWidth = badgeBmp.bmWidth;
  const int badgeHeight = badgeBmp.bmHeight;
  
  // 计算徽章位置（右上角）
  //const int badgeX = std::max(0, baseWidth - badgeWidth);
  //const int badgeY = 0;
  
  const int badgeX = 16;
  const int badgeY = 48;
  
  // 创建32位ARGB兼容位图
  HDC screenDC = GetDC(nullptr);
  HDC memDC = CreateCompatibleDC(screenDC);
  BITMAPINFO bmi = {0};
  bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
  bmi.bmiHeader.biWidth = baseWidth;
  bmi.bmiHeader.biHeight = -baseHeight;  // 负值表示从上到下
  bmi.bmiHeader.biPlanes = 1;
  bmi.bmiHeader.biBitCount = 32;
  bmi.bmiHeader.biCompression = BI_RGB;
  void* pixels = nullptr;
  HBITMAP hCompositeBmp = CreateDIBSection(
      memDC, &bmi, DIB_RGB_COLORS, &pixels, nullptr, 0);
  HBITMAP hOldBmp = (HBITMAP)SelectObject(memDC, hCompositeBmp);
  
  // 绘制原始图标（保留Alpha通道）
  DrawIconEx(memDC, 0, 0, hOriginalIcon, baseWidth, baseHeight, 
             0, nullptr, DI_NORMAL);
  
  // 绘制徽章图标（右上角，保留Alpha混合）
  DrawIconEx(memDC, badgeX, badgeY, num, badgeWidth, badgeHeight, 
             0, nullptr, DI_NORMAL);
  
  // 创建新图标
  ICONINFO newIconInfo = {0};
  newIconInfo.fIcon = TRUE;
  newIconInfo.hbmColor = hCompositeBmp;
  newIconInfo.hbmMask = CreateBitmap(baseWidth, baseHeight, 1, 1, nullptr);
  HICON hCompositeIcon = CreateIconIndirect(&newIconInfo);
  
  // 释放资源
  SelectObject(memDC, hOldBmp);
  DeleteObject(hCompositeBmp);
  DeleteObject(newIconInfo.hbmMask);
  DeleteDC(memDC);
  ReleaseDC(nullptr, screenDC);
  DeleteObject(originalInfo.hbmColor);
  DeleteObject(originalInfo.hbmMask);
  DeleteObject(badgeInfo.hbmColor);
  DeleteObject(badgeInfo.hbmMask);
  
  return hCompositeIcon;
}
```

*   新增函数3：调节ico尺寸大小：

```c

HICON ResizeIconTo(HICON hOriginalIcon, int width) {
   ICONINFO original_info = {0};
   if (!GetIconInfo(hOriginalIcon, &original_info)) {
    return nullptr;
   }
   // 获取原始尺寸
   BITMAP color_bmp = {0};
   GetObject(original_info.hbmColor, sizeof(BITMAP), &color_bmp);
   // const int orig_width = color_bmp.bmWidth;
   // const int orig_height = color_bmp.bmHeight;
   HDC screen_dc = ::GetDC(nullptr);
   HDC target_dc = ::CreateCompatibleDC(screen_dc);
   
   BITMAPINFO bmi = {0};
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth = width;
    bmi.bmiHeader.biHeight = -width;  // Top-down
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = 32;
    void* pixels;
    HBITMAP target_bmp = CreateDIBSection(target_dc, &bmi, DIB_RGB_COLORS, &pixels, 0, 0);
   //HBITMAP target_bmp = ::CreateCompatibleBitmap(screen_dc, width, width);
   HBITMAP old_bmp = (HBITMAP)::SelectObject(target_dc, target_bmp);
   // 透明背景填充（可选）
   RECT rect = {0, 0, width, width};
   ::FillRect(target_dc, &rect, (HBRUSH)GetStockObject(WHITE_BRUSH));
   // 高质量缩放绘制
   ::DrawIconEx(
      target_dc, 0, 0, hOriginalIcon,
      width, width, 0, nullptr, DI_NORMAL);
   // 创建掩码（单色位图）
   HBITMAP mask_bmp = ::CreateBitmap(width, width, 1, 1, nullptr);
   ICONINFO new_info = {0};
   new_info.fIcon = TRUE;             // 图标（非光标）
   new_info.hbmColor = target_bmp;    // 颜色位图
   new_info.hbmMask = mask_bmp;       // 掩码位图
   HICON new_icon = ::CreateIconIndirect(&new_info);
   // 清理资源
   ::SelectObject(target_dc, old_bmp);
   ::DeleteObject(target_bmp);
   ::DeleteObject(mask_bmp);
   ::DeleteDC(target_dc);
   ::ReleaseDC(nullptr, screen_dc);
   ::DeleteObject(original_info.hbmColor);
   ::DeleteObject(original_info.hbmMask);
   return new_icon;   
}

```

##### 3.找到函数：

```c
HICON GetAppIcon() {
  // TODO(mgiuca): Use GetAppIconImageFamily/CreateExact instead of LoadIcon, to
  // get correct scaling. (See http://crbug.com/551256)
  const int icon_id = GetAppIconResourceId();
  // HICON returned from LoadIcon do not leak and do not have to be destroyed.
  return LoadIcon(GetModuleHandle(chrome::kBrowserResourcesDll),
                MAKEINTRESOURCE(icon_id));
```

> 这个函数就是载入任务栏图标icon的函数，感兴趣的小伙伴可以在这里修改，替换ico图片。

##### 4.替换为：

```c
HICON GetAppIcon() {
  // TODO(mgiuca): Use GetAppIconImageFamily/CreateExact instead of LoadIcon, to
  // get correct scaling. (See http://crbug.com/551256)
  const int icon_id = GetAppIconResourceId();
  // HICON returned from LoadIcon do not leak and do not have to be destroyed.

  // 开始追加 ============================
  base::CommandLine* base_command_line = base::CommandLine::ForCurrentProcess();
  //std::string type = base_command_line->GetSwitchValueASCII("type");
  //std::cerr << "=========== type ===========: "<<type  << std::endl;
  if (base_command_line->HasSwitch("notice-number")) {
      int notice_number = 0;
      std::istringstream(base_command_line->GetSwitchValueASCII("notice-number")) >> notice_number;
      std::cerr << "=========== set icon ===========: "  << std::endl;
      HICON resp = LoadIcon(GetModuleHandle(chrome::kBrowserResourcesDll), MAKEINTRESOURCE(icon_id));
      HICON num = CreateNumberIcon(notice_number, 64);
      resp = ResizeIconTo(resp, 96);
      resp = CombineIconWithBadge(resp, num);
      return resp;
  }
  // 结束追加 ============================
  
  return LoadIcon(GetModuleHandle(chrome::kBrowserResourcesDll),
                MAKEINTRESOURCE(icon_id));
}

```

##### 5.编译

```bash
ninja -C out/Default chrome
```

四、备注
----

*   之前记录了一种方法：任务栏图标右上角加提示徽章，是通过找到当前窗口句柄来做的，感兴趣的可以传送：[https://blog.csdn.net/w1101662433/article/details/142182520](https://blog.csdn.net/w1101662433/article/details/142182520)

