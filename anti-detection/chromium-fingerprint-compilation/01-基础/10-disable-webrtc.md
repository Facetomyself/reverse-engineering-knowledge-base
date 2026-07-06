修改chromium-禁用webRTC
-------------------

#### 一、WebRTC指纹是什么

*   之前介绍过webRTC和如何修改webRTC的ip识别： https://blog.csdn.net/w1101662433/article/details/138001797

#### 二、编译源码禁用webRTC

*   第一篇文章写了如何编译chromium，假设你已经编译成功了。
*   找到源码 `\third_party\blink\renderer\modules\peerconnection\rtc_peer_connection.cc`

###### 1.找到下面的代码

```c
ScriptPromise<IDLUndefined> RTCPeerConnection::setLocalDescription(
    ScriptState* script_state,
    const RTCSessionDescriptionInit* session_description_init,
    ExceptionState& exception_state) {
  if (closed_) {
    exception_state.ThrowDOMException(DOMExceptionCode::kInvalidStateError,
                                      kSignalingStateClosedMessage);
    return EmptyPromise();
  }
```

###### 2.替换为

```c
ScriptPromise<IDLUndefined> RTCPeerConnection::setLocalDescription(
    ScriptState* script_state,
    const RTCSessionDescriptionInit* session_description_init,
    ExceptionState& exception_state) {
  if (!closed_) {
    exception_state.ThrowDOMException(DOMExceptionCode::kInvalidStateError,
                                      kSignalingStateClosedMessage);
    return EmptyPromise();
  }

//if (closed_) {
  //  exception_state.ThrowDOMException(DOMExceptionCode::kInvalidStateError,
  //                                    kSignalingStateClosedMessage);
  //  return ScriptPromise();
  //}
```

> 原理就是将webrtc的正常运行逻辑强行打断，无法正确返回。

###### 3.编译

```
ninja  -C  out/Default chrome
```

*   编译后再也没有网站可以窥探我的真实ip了，舒坦。

#### 三、在线指纹验证网站：

*   https://browserleaks.com/webrtc
*   https://www.browserscan.net/

#### 四、2025-05-08补充

*   群友提供了更优秀的禁用方案，只需要启动时带上这2个参数即可：

```sh
./chrome.exe
--force-webrtc-ip-handling-policy
--webrtc-ip-handling-policy=disable_non_proxied_udp
```
