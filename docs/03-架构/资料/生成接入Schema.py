"""生成manifest与桥消息JSON Schema；不生成游戏或SDK实现。"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
api = json.loads((BASE / "资料/平台OpenAPI-V0.1.json").read_text())
defs = api["components"]["schemas"]


def ref(name):
    return {"$ref": "#/$defs/" + name}


def obj(props, required=None):
    return {"type": "object", "additionalProperties": False, "properties": props,
            "required": list(props) if required is None else required}


def text(maximum=128, minimum=1, **kw):
    return {"type": "string", "minLength": minimum, "maxLength": maximum, **kw}


def array(items, minimum=0, maximum=1000):
    return {"type": "array", "items": items, "minItems": minimum, "maxItems": maximum}


key = text(pattern="^[A-Za-z0-9._:-]+$")
save_format = text(pattern="^[!-~]+$")
uuid = text(36, 36, format="uuid")
path = text(512, pattern="^(?!/)(?!.*(?:^|/)\\.\\.(?:/|$))(?!.*\\\\)[^?#\\x00]+$")
manifest = obj({
    "manifestVersion": {"const": "1.0"},
    "gameKey": key, "gameVersion": key,
    "platformProtocol": obj({"min": {"const": "1.0"}, "max": {"const": "1.x"}}),
    "entry": path,
    "capabilities": array({"enum": ["context", "access", "resources", "purchase", "save", "events", "return"]}, 1, 7),
    "save": obj({"format": save_format, "accepts": array(save_format, 1, 30), "maxBytes": {"const": 1048576}}),
    "routes": obj({"mode": {"enum": ["spa", "document"]}, "fallback": path}, ["mode"]),
    "content": array(obj({"key": key, "availability": {"enum": ["trial", "entitled"]}}), 1),
    "resources": array(obj({"path": path, "visibility": {"enum": ["public", "protected"]},
                            "requiresAll": array(key, 1), "resourceId": uuid,
                            "sha256": text(64, 64, pattern="^[a-f0-9]{64}$")},
                           ["path", "visibility"]), 1, 10000),
}, ["manifestVersion", "gameKey", "gameVersion", "platformProtocol", "entry", "capabilities", "routes", "content", "resources"])
manifest["properties"]["capabilities"]["uniqueItems"] = True
resource = manifest["properties"]["resources"]["items"]
resource["allOf"] = [
    {"if": {"properties": {"visibility": {"const": "protected"}}},
     "then": {"required": ["requiresAll"]},
     "else": {"not": {"required": ["requiresAll"]}}},
]
manifest.update({
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://schema.invalid/xj/manifest/1.0",
    "title": "间隙PLAY游戏资源包声明草案",
    "x-cross-field-validation": [
        "URL解码/Unicode及大小写碰撞、符号链接、解压穿越由发布验证器拒绝；正则不能替代安全归一化",
        "resource.path与content.key分别唯一；requiresAll均属于当前作品；entry/fallback必须在公开清单",
        "资源manifestVersion与平台支持major匹配；save存在当且仅当声明save能力",
        "resourceId由平台在发布索引中分配，上传者不能伪造归属；包内摘要逐文件比对",
        "10000文件/30格式是待资源确认的设计上限，不当作已批准生产额度",
    ],
})
(BASE / "资料/游戏Manifest-Schema-V0.1.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

methods = {
    "context.get": ("Empty", "Run"),
    "access.check": ("AccessRequest", "AccessResult"),
    "resources.read": ("ResourceRead", "ResourceTransfer"),
    "purchase.request": ("BridgePurchase", "PurchaseIntent"),
    "purchase.status": ("BridgeIntentId", "PurchaseIntent"),
    "save.describe": ("Empty", "SaveDescription"),
    "save.read": ("SaveRead", "SavePayload"),
    "save.write": ("BridgeWrite", "SaveOperation"),
    "save.import": ("BridgeImport", "SaveOperation"),
    "save.restore": ("BridgeRestore", "SaveOperation"),
    "save.restart": ("BridgeRestart", "SaveOperation"),
    "save.operation": ("BridgeOperation", "SaveOperation"),
    "save.restoreConfirm": ("BridgeRestoreConfirm", "SaveOperation"),
    "events.report": ("GameEvents", "EventReceipt"),
    "runtime.ready": ("Ready", "Run"),
    "runtime.exit": ("Exit", "Acknowledgement"),
    "platform.return": ("Exit", "Acknowledgement"),
}
defs["BridgePurchase"] = obj({"contentKeys": array(key, 1), "resumeHandle": text(2048, 0)}, ["contentKeys"])
defs["BridgeIntentId"] = obj({"intentId": uuid})
defs["BridgeOperation"] = obj({"operationId": uuid})
defs["BridgeRestoreConfirm"] = obj({"operationId": uuid, "compatible": {"type": "boolean"},
                                  "failureCategory": key}, ["operationId", "compatible"])
for method, action in [("Write", "WRITE"), ("Import", "IMPORT"), ("Restore", "RESTORE"), ("Restart", "RESTART")]:
    fields = {"baseRevision": text(20, pattern="^(0|[1-9][0-9]{0,19})$"), "operationId": key}
    if action in ("WRITE", "IMPORT"):
        fields.update(format=save_format, payloadBase64=text(1398104, 0, contentEncoding="base64"))
    if action == "RESTORE":
        fields["sourceBlobId"] = uuid
    if action in ("IMPORT", "RESTORE", "RESTART"):
        fields["confirmed"] = {"const": True}
    defs["Bridge" + method] = obj(fields)
safe_size = {"type": "integer", "minimum": 0, "maximum": 9007199254740991}
positive_size = {**safe_size, "minimum": 1}
defs["ResourceTransfer"] = obj({"resourceId": uuid, "mime": text(128), "byteLength": safe_size,
                              "sha256": text(64, 64, pattern="^[a-f0-9]{64}$"), "transferId": key,
                              "chunkBytes": positive_size, "chunkCount": positive_size})
requests, responses = [], []
for method, (params, result) in methods.items():
    envelope = {"protocolVersion": {"const": "1.0"}, "channelId": key,
                "requestId": key, "method": {"const": method}}
    requests.append(obj({**envelope, "params": ref(params)}))
    responses += [
        obj({**envelope, "ok": {"const": True}, "result": ref(result)}),
        obj({**envelope, "ok": {"const": False}, "error": ref("Error")}),
    ]
hello = obj({"type": {"const": "HELLO"}, "protocolVersion": {"const": "1.0"},
             "gameVersion": key})
init = obj({"type": {"const": "INIT"}, "protocolVersion": {"const": "1.0"},
            "channelId": key, "run": ref("Run")})
invalidate = obj({"type": {"const": "INVALIDATE"}, "channelId": key,
                  "reason": {"enum": ["AUTH_EXPIRED", "ACCOUNT_CHANGED", "RUN_CLOSED", "FRAME_NAVIGATED", "ACCESS_CHANGED", "SUSPENDED"]}})
transfer_context = {"protocolVersion": {"const": "1.0"}, "channelId": key,
                    "requestId": key, "transferId": key, "resourceId": uuid}
chunk_header = obj({**transfer_context, "type": {"const": "RESOURCE_CHUNK"},
                    "chunkIndex": safe_size, "byteOffset": safe_size,
                    "byteLength": safe_size, "final": {"type": "boolean"}})
resource_ack = obj({**transfer_context, "type": {"const": "RESOURCE_ACK"},
                    "action": {"enum": ["CONTINUE", "COMPLETE", "CANCEL"]},
                    "chunkIndex": safe_size}, [*transfer_context, "type", "action"])
resource_ack["allOf"] = [
    {"if": {"properties": {"action": {"enum": ["CONTINUE", "COMPLETE"]}}},
     "then": {"required": ["chunkIndex"]}}
]
resource_abort = obj({**transfer_context, "type": {"const": "RESOURCE_ABORT"},
                      "reason": {"enum": ["CANCELLED", "TIMEOUT", "LIMIT_EXCEEDED", "INVALID_FRAME",
                                          "INTEGRITY_FAILED", "ACCESS_CHANGED", "SOURCE_FAILED"]}})
bridge = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://schema.invalid/xj/bridge/1.0",
    "title": "宿主与独立游戏消息契约草案",
    "$defs": {**defs, "Request": {"oneOf": requests}, "Response": {"oneOf": responses},
              "Hello": hello, "Init": init, "Invalidate": invalidate,
              "ResourceChunkHeader": chunk_header, "ResourceAck": resource_ack, "ResourceAbort": resource_abort},
    "oneOf": [ref(n) for n in ("Request", "Response", "Hello", "Init", "Invalidate", "ResourceAck", "ResourceAbort")],
    "x-authentication": "Schema不验证origin/frame/port或身份，接收者必须独立核验准确来源与当前窗口",
    "x-binary": "resources.read先返回ResourceTransfer；后续同一MessagePort发送{header,buffer:ArrayBuffer}，仅header由$defs.ResourceChunkHeader校验，该原生帧不属于根JSON oneOf；接收者另查buffer类型/长度/连续偏移/分块序号/final/完整摘要；每传输最多1块未ACK，末块验完回COMPLETE，取消回CANCEL，宿主终止回RESOURCE_ABORT",
    "x-cross-field-validation": [
        "Run.resourceIndex仅当前固定版本的受控资源；path/resourceId各自唯一、与已发布索引逐项对应；索引不是授权，路径不承诺保密",
        "chunkCount=max(1,ceil(byteLength/chunkBytes))；零字节资源为1块，长度0/final=true；chunkBytes不得超过宿主配置",
        "同port/channel/request/transfer/resource配对；从chunkIndex=0及byteOffset=0连续无重叠覆盖，final当且仅当最后一块；完成后总长度与sha256一致",
        "ACK只能确认本次唯一未确认块；COMPLETE只用于完整摘要通过的末块，CONTINUE只用于非末块；重复/越序/未知帧拒绝并清理",
        "单资源/全局在途/缓冲总量及超时必须先配置；超限在分配前拒绝；JSON Schema不能证明内存边界和授权",
    ],
    "x-idempotency": "requestId为本端口RPC关联；持久动作operationId及宿主Idempotency-Key另行绑定；游戏不能指定主体",
    "x-limits-proposal": "非资源RPC<=2MiB、同时最多8个未完成调用、20秒通信超时为待压测建议；超时先查原操作，不生成第二付款或保存",
}
raw = json.dumps(bridge, ensure_ascii=False, indent=2).replace("#/components/schemas/", "#/$defs/")
(BASE / "资料/游戏消息桥Schema-V0.1.json").write_text(raw + "\n")
print(f"生成manifest及{len(methods)}个RPC方法的双向消息schema；均未实现")
