## 通用信息
### 调用域名
https://api.klingai.com

### 接口鉴权
- Step-1：获取 AccessKey + SecretKey
- Step-2：您每次请求API的时候，需要按照固定加密方法生成API Token
	- 加密方法：遵循JWT（Json Web Token, RFC 7519）标准
	- JWT由三个部分组成：Header、Payload、Signature
	- 示例代码（Python）：

```python
import time
import jwt

ak = "" # 填写access key
sk = "" # 填写secret key

def encode_jwt_token(ak, sk):
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 1800, # 有效时间，此处示例代表当前时间+1800s(30min)
        "nbf": int(time.time()) - 5 # 开始生效的时间，此处示例代表当前时间-5秒
    }
    token = jwt.encode(payload, sk, headers=headers)
    return token

api_token = encode_jwt_token(ak, sk)
print(api_token) # 打印生成的API_TOKEN
```
- Step-3：用第二步生成的API Token组装成Authorization，填写到 Request Header 里
组装方式：Authorization = "Bearer XXX"， 其中XXX填写第二步生成的API Token（注意Bearer跟XXX之间有空格）

## 视频生成
### 【文生视频】
#### 创建任务网络协议	https
请求地址	/v1/videos/text2video
请求方法	POST
请求格式	application/json
响应格式	application/json

#### 请求头
字段	值	描述
Content-Type	application/json	数据交换格式
Authorization	鉴权信息，参考接口鉴权	鉴权信息，参考接口鉴权

请您注意，为了保持命名统一，原 model字段变更为 model_name字段，未来请您使用该字段来指定需要调用的模型版本。
同时，我们保持了行为上的向前兼容，如您继续使用原 model字段，不会对接口调用有任何影响、不会有任何异常，等价于 model_name为空时的默认行为（即调用V1模型）

#### 请求体
| 字段                                                                       | 类型   | 必填 | 默认值   | 描述                                                                                   |
| -------------------------------------------------------------------------- | ------ | ---- | -------- | -------------------------------------------------------------------------------------- |
| model_name                                                                 | string | 可选 | kling-v1 | 模型名称                                                                               |
| 枚举值：kling-v1, kling-v1-6                                               |        |      |          |                                                                                        |
| prompt                                                                     | string | 必须 | 无       | 正向文本提示词                                                                         |
| 不能超过2500个字符                                                         |        |      |          |                                                                                        |
| negative_prompt                                                            | string | 可选 | 空       | 负向文本提示词                                                                         |
| 不能超过2500个字符                                                         |        |      |          |                                                                                        |
| cfg_scale                                                                  | float  | 可选 | 0.5      | 生成视频的自由度；值越大，模型自由度越小，与用户输入的提示词相关性越强                 |
| 取值范围：[0, 1]                                                           |        |      |          |                                                                                        |
| mode                                                                       | string | 可选 | std      | 生成视频的模式                                                                         |
| 枚举值：std，pro                                                           |        |      |          |                                                                                        |
| 其中std：标准模式（标准），基础模式，性价比高                              |        |      |          |                                                                                        |
| 其中pro：专家模式（高品质），高表现模式，生成视频质量更佳                  |        |      |          |                                                                                        |
| 不同模型版本、视频模式支持范围不同，详见当前文档3-0能力地图                |        |      |          |                                                                                        |
| camera_control                                                             | object | 可选 | 空       | 控制摄像机运动的协议（如未指定，模型将根据输入的文本/图片进行智能匹配）                |
| 不同模型版本、视频模式支持范围不同，详见当前文档3-0能力地图                |        |      |          |                                                                                        |
| camera_control                                                             | string | 可选 | 无       | 预定义的运镜类型                                                                       |
| type                                                                       |        |      |          | 枚举值："simple", "down_back", "forward_up", "right_turn_forward", "left_turn_forward" |
| simple：简单运镜，此类型下可在"config"中六选一进行运镜                     |        |      |          |                                                                                        |
| down_back：镜头下压并后退 ➡️ 下移拉远，此类型下config参数无需填写           |        |      |          |                                                                                        |
| forward_up：镜头前进并上仰 ➡️ 推进上移，此类型下config参数无需填写          |        |      |          |                                                                                        |
| right_turn_forward：先右旋转后前进 ➡️ 右旋推进，此类型下config参数无需填写  |        |      |          |                                                                                        |
| left_turn_forward：先左旋并前进 ➡️ 左旋推进，此类型下config参数无需填写     |        |      |          |                                                                                        |
| camera_control                                                             | object | 可选 | 无       | 包含六个字段，用于指定摄像机在不同方向上的运动或变化                                   |
| config                                                                     |        |      |          | 当运镜类型指定simple时必填，指定其他类型时不填                                         |
| 以下参数6选1，即只能有一个参数不为0，其余参数为0                           |        |      |          |                                                                                        |
| config                                                                     | float  | 可选 | 无       | 水平运镜，控制摄像机在水平方向上的移动量（沿x轴平移）                                  |
| horizontal                                                                 |        |      |          | 取值范围：[-10, 10]，负值表示向左平移，正值表示向右平移                                |
| config                                                                     | float  | 可选 | 无       | 垂直运镜，控制摄像机在垂直方向上的移动量（沿y轴平移）                                  |
| vertical                                                                   |        |      |          | 取值范围：[-10, 10]，负值表示向下平移，正值表示向上平移                                |
| config                                                                     | float  | 可选 | 无       | 水平摇镜，控制摄像机在水平面上的旋转量（绕y轴旋转）                                    |
| pan                                                                        |        |      |          | 取值范围：[-10, 10]，负值表示绕y轴向左旋转，正值表示绕y轴向右旋转                      |
| config                                                                     | float  | 可选 | 无       | 垂直摇镜，控制摄像机在垂直面上的旋转量（沿x轴旋转）                                    |
| tilt                                                                       |        |      |          | 取值范围：[-10, 10]，负值表示绕x轴向下旋转，正值表示绕x轴向上旋转                      |
| config                                                                     | float  | 可选 | 无       | 旋转运镜，控制摄像机的滚动量（绕z轴旋转）                                              |
| roll                                                                       |        |      |          | 取值范围：[-10, 10]，负值表示绕z轴逆时针旋转，正值表示绕z轴顺时针旋转                  |
| config                                                                     | float  | 可选 | 无       | 变焦，控制摄像机的焦距变化，影响视野的远近                                             |
| zoom                                                                       |        |      |          | 取值范围：[-10, 10]，负值表示焦距变长、视野范围变小，正值表示焦距变短、视野范围变大    |
| aspect_ratio                                                               | string | 可选 | 16:09    | 生成视频的画面纵横比（宽:高）                                                          |
| 枚举值：16:9, 9:16, 1:1                                                    |        |      |          |                                                                                        |
| duration                                                                   | string | 可选 | 5        | 生成视频时长，单位s                                                                    |
| 枚举值：5，10                                                              |        |      |          |                                                                                        |
| callback_url                                                               | string | 可选 | 无       | 本次任务结果回调通知地址，如果配置，服务端会在任务状态发生变更时主动通知               |
| 具体通知的消息schema见“Callback协议”                                       |        |      |          |                                                                                        |
| external_task_id                                                           | string | 可选 | 无       | 自定义任务ID                                                                           |
| 用户自定义任务ID，传入不会覆盖系统生成的任务ID，但支持通过该ID进行任务查询 |        |      |          |                                                                                        |
| 请注意，单用户下需要保证唯一性                                             |        |      |          |                                                                                        |
#### 响应体
```json
{
	"code": 0, //错误码；具体定义见错误码
  "message": "string", //错误信息
  "request_id": "string", //请求ID，系统生成，用于跟踪请求、排查问题
  "data":{
  	"task_id": "string", //任务ID，系统生成
    "task_info":{ //任务创建时的参数信息
       "external_task_id": "string"//客户自定义任务ID
    }, 
    "task_status": "string", //任务状态，枚举值：submitted（已提交）、processing（处理中）、succeed（成功）、failed（失败）
    "created_at": 1722769557708, //任务创建时间，Unix时间戳、单位ms
    "updated_at": 1722769557708 //任务更新时间，Unix时间戳、单位ms
  }
}
```

### 【文生视频】查询任务（单个）

网络协议	https
请求地址	/v1/videos/text2video/{id}
请求方法	GET
请求格式	application/json
响应格式	application/json

#### 请求头
字段	值	描述
Content-Type	application/json	数据交换格式
Authorization	鉴权信息，参考接口鉴权	鉴权信息，参考接口鉴权

#### 请求路径参数
字段	类型	必填	默认值	描述
task_id	string	可选	无	文生视频的任务ID ● 请求路径参数，直接将值填写在请求路径中，与external_task_id两种查询方式二选一
external_task_id	string	可选	无	文生视频的自定义任务ID ● 创建任务时填写的external_task_id，与task_id两种查询方式二选一

#### 请求体
无

#### 响应体
```json
{
	"code": 0, //错误码；具体定义见错误码
  "message": "string", //错误信息
  "request_id": "string", //请求ID，系统生成，用于跟踪请求、排查问题
  "data":{
  	"task_id": "string", //任务ID，系统生成 
    "task_status": "string", //任务状态，枚举值：submitted（已提交）、processing（处理中）、succeed（成功）、failed（失败）
    "task_status_msg": "string", //任务状态信息，当任务失败时展示失败原因（如触发平台的内容风控等）
    "task_info": { //任务创建时的参数信息
      "external_task_id": "string"//客户自定义任务ID
    },
    "task_result":{
      "videos":[
        {
        	"id": "string", //生成的视频ID；全局唯一
      		"url": "string", //生成视频的URL，例如https://p1.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_46554461/-2878350957757294165/output.mp4（请注意，为保障信息安全，生成的图片/视频会在30天后被清理，请及时转存）
      		"duration": "string" //视频总时长，单位s
        }
      ]
    }
    "created_at": 1722769557708, //任务创建时间，Unix时间戳、单位ms
    "updated_at": 1722769557708, //任务更新时间，Unix时间戳、单位ms
  }
}
```

