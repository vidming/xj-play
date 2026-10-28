"""静态架构检查与拒绝样本；不连库、不启动业务、不调用渠道。"""
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zoneinfo import ZoneInfo

import jsonschema

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "docs/README.md").is_file())
BASE = ROOT / "docs/03-架构"
SOURCE = BASE / "05-资料"
checks = {}


def read(name):
    return json.loads((SOURCE / name).read_text())


def walk(value, root):
    if isinstance(value, dict):
        if "$ref" in value and value["$ref"].startswith("#/"):
            target = root
            for key in value["$ref"][2:].split("/"):
                target = target[key.replace("~1", "/").replace("~0", "~")]
        for child in value.values():
            walk(child, root)
    elif isinstance(value, list):
        for child in value:
            walk(child, root)


api = read("平台OpenAPI-V0.1.json")
meta = read("OpenAPI官方元模式-20250915.json")
jsonschema.Draft202012Validator(meta).validate(api)
walk(api, api)
operation_ids = []
for path, item in api["paths"].items():
    for method, operation in item.items():
        operation_ids.append(operation["operationId"])
        path_params = {p["name"] for p in operation["parameters"] if p["in"] == "path"}
        assert set(re.findall(r"{([^}]+)}", path)) == path_params
        if "/admin-api/" in path:
            assert operation["security"] == [{"adminBearer": []}]
            assert operation["x-authorization"].startswith("xj:")
        if "/notifications/" not in path and method != "get":
            assert any(p["name"] == "Idempotency-Key" and p["required"] for p in operation["parameters"])
assert len(set(operation_ids)) == len(operation_ids)
accepted_operations = [operation["operationId"] for item in api["paths"].values()
                       for operation in item.values() if "202" in operation["responses"]]
assert accepted_operations == ["operateSave"], accepted_operations
save_responses = api["paths"]["/app-api/xj/v1/runs/{runId}/save-operations"]["post"]["responses"]
assert save_responses["202"]["content"] == save_responses["200"]["content"]
resource_responses = api["paths"]["/app-api/xj/v1/runs/{runId}/resources/read"]["post"]["responses"]
assert "202" not in resource_responses
assert "application/octet-stream" in resource_responses["200"]["content"]
checks["OpenAPI官方元模式与引用"] = f"通过；{len(operation_ids)}个唯一操作；未运行服务"
checks["异步受理形状"] = "仅显式声明的存档提交使用202/SaveOperation，按id查询；资源读取只返回二进制或错误，无悬空202"
restriction_operations = {"logoutPlayer", "completeReset", "requestDeletion", "confirmDeletion", "adminChangeGameState", "adminExecutePlan"}
for item in api["paths"].values():
    for operation in item.values():
        if operation["operationId"] in restriction_operations:
            assert "同一事务" in operation["x-restriction-completion"]
            assert "原Idempotency-Key" in operation["description"]
            assert "503" in operation["responses"]
checks["限制完成语义"] = "6个现有操作（含重置口令撤会话）注明SD2同库提交与未明语义；不新增内部日志API或游戏RPC；仅静态文案检查"
checks["官方元模式来源"] = "https://spec.openapis.org/oas/3.1/schema/2025-09-15；2026-10-25实际HTTP200读取"

schemas = api["components"]["schemas"]
for sch in schemas.values():
    jsonschema.Draft202012Validator.check_schema(sch)
standalone = {}
for name in ["平台事件Schema-V0.1.json", "游戏Manifest-Schema-V0.1.json", "游戏消息桥Schema-V0.1.json"]:
    doc = read(name)
    jsonschema.Draft202012Validator.check_schema(doc)
    walk(doc, doc)
    standalone[name] = doc
checks["Schema结构"] = f"OpenAPI {len(schemas)}个schema＋3份独立Schema元模式与本地引用通过"

prd = (ROOT / "docs/02-产品与设计/01-产品规划/01-文档/间隙PLAY-产品需求文档-V1.0-提交稿.md").read_text()
section = prd.split("## 5. 核心事件埋点字典表")[1].split("## 6.")[0]
product_events = set(re.findall(r"^\| ([a-z][a-z_]+) \|", section, re.M))
contract_events = {n.removeprefix("Event_") for n in schemas if n.startswith("Event_")}
assert len(product_events) == 31 and product_events == contract_events
checks["产品事件对应"] = "31项名称与固定PRD完全对应；businessRef按实际确认追加"

sample_checks = []
uuid = "00000000-0000-4000-8000-000000000001"
validator_options = {"format_checker": jsonschema.FormatChecker()}


def api_valid(name, value, valid):
    doc = {"$ref": "#/components/schemas/" + name, "components": api["components"]}
    result = jsonschema.Draft202012Validator(doc, **validator_options).is_valid(value)
    assert result is valid, (name, value, result)
    sample_checks.append({"schema": name, "expectedValid": valid})


def assert_static_case_structure(case):
    assert set(case) <= {"case", "request", "value", "schemaValid", "amountRelationValid", "given", "expect"}, case
    assert isinstance(case["case"], str) and case["case"]
    assert isinstance(case["schemaValid"], bool)
    assert ("request" in case) != ("value" in case), case
    assert isinstance(case.get("given"), str) and case["given"]
    assert isinstance(case.get("expect"), str) and case["expect"]
    if "amountRelationValid" in case:
        assert isinstance(case["amountRelationValid"], bool)
        value = case["value"]
        actual = (0 <= value["creditFen"] <= value["priceFen"]
                  and value["dueFen"] == value["priceFen"] - value["creditFen"])
        assert actual is case["amountRelationValid"], case


static_case_count = 0
for path, item in api["paths"].items():
    for operation in item.values():
        if "x-static-cases" not in operation:
            continue
        request_schema = operation["requestBody"]["content"]["application/json"]["schema"]["$ref"].rsplit("/", 1)[1]
        for case in operation["x-static-cases"]:
            assert_static_case_structure(case)
            assert "request" in case, (path, case)
            api_valid(request_schema, case["request"], case["schemaValid"])
            static_case_count += 1
for name, schema in schemas.items():
    for case in schema.get("x-static-cases", []):
        assert_static_case_structure(case)
        assert "value" in case, (name, case)
        api_valid(name, case["value"], case["schemaValid"])
        static_case_count += 1
checks["操作与Schema静态用例"] = f"{static_case_count}条逐例请求/载荷Schema断言；金额关系独立断言，非文案关键字检查"


def standalone_valid(name, value, valid):
    result = jsonschema.Draft202012Validator(standalone[name], **validator_options).is_valid(value)
    assert result is valid, (name, value, result)
    sample_checks.append({"schema": name, "expectedValid": valid})


def bridge_def_valid(name, value, valid):
    bridge = standalone["游戏消息桥Schema-V0.1.json"]
    doc = {"$ref": "#/$defs/" + name, "$defs": bridge["$defs"]}
    result = jsonschema.Draft202012Validator(doc, **validator_options).is_valid(value)
    assert result is valid, (name, value, result)
    sample_checks.append({"schema": "Bridge." + name, "expectedValid": valid})


api_valid("PaymentCreate", {"channel": "ALIPAY", "method": "PAGE"}, True)
api_valid("PaymentCreate", {"channel": "WECHAT", "method": "NATIVE"}, True)
api_valid("PaymentCreate", {"channel": "WECHAT", "method": "WAP"}, False)
api_valid("PaymentCreate", {"channel": "WECHAT", "method": "JSAPI"}, False)
api_valid("PaymentCreate", {"channel": "ALIPAY", "method": "PAGE", "paid": True}, False)
api_valid("RunCreate", {"gameId": uuid, "entryMode": "TRIAL"}, True)
api_valid("RunCreate", {"gameId": uuid, "entryMode": "TRIAL", "playerId": uuid}, False)
api_valid("RunCreate", {"gameId": uuid, "entryMode": "TRIAL", "intentId": uuid}, True)
api_valid("Login", {"email": "player@example.com", "password": "a" * 15, "intentId": uuid}, True)
api_valid("Login", {"email": "player@example.com", "password": "a" * 15, "guestSessionId": uuid}, False)
api_valid("Login", {"email": "player@example.com", "password": "a" * 15, "intentId": "invalid"}, False)
api_valid("PurchaseIntentCreate", {"runId": uuid, "contentKeys": ["story.main"]}, True)
api_valid("PurchaseIntentCreate", {"runId": uuid, "contentKeys": ["story.main"], "subjectId": uuid}, False)
api_valid("RunResume", {"state": "UNAVAILABLE", "reason": "NO_SAVED_POSITION"}, True)
api_valid("RunResume", {"state": "UNAVAILABLE", "reason": "NO_SAVED_POSITION", "handle": "position"}, False)
api_valid("RunResume", {"state": "AVAILABLE", "handle": "position", "versionId": uuid,
                        "expiresAt": "2026-10-26T18:00:00Z"}, True)
api_valid("RunResume", {"state": "AVAILABLE", "handle": "position", "versionId": uuid,
                        "expiresAt": "2026-10-26T18:00:00Z", "reason": "EXPIRED"}, False)
api_valid("ContinueSummary", {"available": True, "saveState": "AVAILABLE", "accessState": "ALLOWED",
                              "versionId": uuid, "lastActivityAt": "2026-10-26T18:00:00Z"}, True)
api_valid("ContinueSummary", {"available": True, "saveState": "CONFLICT", "accessState": "ALLOWED",
                              "versionId": uuid, "lastActivityAt": "2026-10-26T18:00:00Z"}, False)
api_valid("ContinueSummary", {"available": False, "saveState": "CONFLICT",
                              "accessState": "DENIED"}, True)
api_valid("QuoteConfirm", {"quoteId": uuid, "expectedAccessRevision": "1"}, True)
api_valid("QuoteConfirm", {"quoteId": uuid, "expectedAccessRevision": "1", "priceFen": 1}, False)
api_valid("Empty", {}, True)
api_valid("Empty", {"unexpected": None}, False)
api_valid("LoginResult", {"state": "SUCCEEDED"}, True)
api_valid("LoginResult", {"state": "SUCCEEDED", "handoffError": {"code": "INTENT_BINDING_INVALID", "msg": "暂时无法交接购买返回"}}, True)
api_valid("LoginResult", {"state": "FAILED", "handoffError": {"code": "INTENT_BINDING_INVALID", "msg": "意图已取消"}}, False)
api_valid("LoginResult", {"state": "SUCCEEDED", "handoffError": {"code": "CANCELLED", "msg": "意图已取消"}}, False)
valid_upgrade = {"id": uuid, "gameId": uuid, "productRevisionId": uuid, "priceFen": 1000,
                 "creditFen": 1000, "dueFen": 0, "currency": "CNY", "promise": "买断全部已发布章节",
                 "contentKeys": ["story.main"], "state": "RESERVED"}
api_valid("Upgrade", valid_upgrade, True)
api_valid("Upgrade", {k: v for k, v in valid_upgrade.items() if k != "productRevisionId"}, False)
api_valid("Upgrade", {k: v for k, v in valid_upgrade.items() if k != "promise"}, False)
api_valid("Upgrade", {**valid_upgrade, "orderId": uuid}, False)
api_valid("Upgrade", {**valid_upgrade, "state": "DELIVERED"}, False)
api_valid("Upgrade", {**valid_upgrade, "state": "DELIVERED", "grantId": uuid}, True)
api_valid("SaveWrite", {"action": "WRITE", "baseRevision": "0"}, False)
api_valid("SaveWrite", {"action": "WRITE", "baseRevision": "0", "format": "ga/1", "payloadBase64": ""}, True)
api_valid("SaveWrite", {"action": "RESTART", "baseRevision": "0", "confirmed": False}, False)
api_valid("SaveWrite", {"action": "RESTART", "baseRevision": "0", "confirmed": True}, True)
api_valid("SaveWrite", {"action": "READ_RESTORE", "baseRevision": "0", "sourceBlobId": uuid, "confirmed": True}, False)
api_valid("SupportCreate", {"businessRef": {"type": "upgrade", "id": uuid}, "category": "REVOKE", "description": "零补款售后"}, True)
api_valid("SupportCreate", {"businessRef": {"type": "paid", "id": uuid}, "category": "REVOKE", "description": "错误类型"}, False)
event = {"event_ref": "e-1", "type": "order_payment_success", "occurred_at": "2026-10-25T00:00:00Z",
         "fields": {"order_ref": "o-1", "payment_ref": "p-1"}}
api_valid("Event", event, True)
api_valid("GameEvents", {"events": [event]}, False)
support_event = {"event_ref": "e-2", "type": "support_request_success", "occurred_at": "2026-10-25T00:00:00Z",
                 "fields": {"businessRef": {"type": "grant", "id": uuid}}}
api_valid("Event", support_event, True)
api_valid("Event", {**support_event, "fields": {"order_ref": "placeholder"}}, False)
manifest = {
    "manifestVersion": "1.0", "gameKey": "ga", "gameVersion": "1.0.0",
    "platformProtocol": {"min": "1.0", "max": "1.x"}, "entry": "index.html",
    "capabilities": ["context", "access"], "routes": {"mode": "spa", "fallback": "index.html"},
    "content": [{"key": "story.main", "availability": "entitled"}],
    "resources": [{"path": "index.html", "visibility": "public"},
                  {"path": "content/main.bin", "visibility": "protected", "requiresAll": ["story.main"]}],
}
standalone_valid("游戏Manifest-Schema-V0.1.json", manifest, True)
standalone_valid("游戏Manifest-Schema-V0.1.json", {**manifest, "entry": "../outside.html"}, False)
standalone_valid("游戏Manifest-Schema-V0.1.json", {**manifest, "resources": [{"path": "secret", "visibility": "protected"}]}, False)
request = {"protocolVersion": "1.0", "channelId": "ch-1", "requestId": "rpc-1",
           "method": "access.check", "params": {"contentKeys": ["story.main"]}}
standalone_valid("游戏消息桥Schema-V0.1.json", request, True)
standalone_valid("游戏消息桥Schema-V0.1.json", {**request, "params": {"contentKeys": ["story.main"], "playerId": uuid}}, False)
standalone_valid("游戏消息桥Schema-V0.1.json", {**request, "method": "setPaid"}, False)
run = {"id": uuid, "gameId": uuid, "versionId": uuid, "mode": "TRIAL",
       "gameOrigin": "https://game.invalid", "entryUrl": "https://game.invalid/index.html",
       "protocolVersion": "1.0", "capabilities": ["resources"], "accessRevision": "1",
       "expiresAt": "2026-10-25T18:00:00Z", "state": "AUTHORIZED",
       "resourceIndex": [{"path": "content/r001.bin", "resourceId": uuid}]}
api_valid("Run", run, True)
api_valid("Run", {k: v for k, v in run.items() if k != "resourceIndex"}, False)
api_valid("Run", {**run, "resourceIndex": [{"path": "../secret", "resourceId": uuid}]}, False)
api_valid("Run", {**run, "resourceIndex": [{"path": "content/r001.bin", "resourceId": uuid, "paid": True}]}, False)
standalone_valid("游戏消息桥Schema-V0.1.json",
                 {"type": "INIT", "protocolVersion": "1.0", "channelId": "ch-1", "run": run}, True)
transfer = {"resourceId": uuid, "mime": "application/octet-stream", "byteLength": 0,
            "sha256": hashlib.sha256(b"").hexdigest(), "transferId": "t-1", "chunkBytes": 65536, "chunkCount": 1}
bridge_def_valid("ResourceTransfer", transfer, True)
bridge_def_valid("ResourceTransfer", {**transfer, "chunkBytes": 0}, False)
bridge_def_valid("ResourceTransfer", {**transfer, "byteLength": 9007199254740992}, False)
transport = {"protocolVersion": "1.0", "channelId": "ch-1", "requestId": "rpc-2",
             "transferId": "t-1", "resourceId": uuid}
header = {**transport, "type": "RESOURCE_CHUNK", "chunkIndex": 0,
          "byteOffset": 0, "byteLength": 0, "final": True}
bridge_def_valid("ResourceChunkHeader", header, True)
bridge_def_valid("ResourceChunkHeader", {**header, "chunkIndex": -1}, False)
bridge_def_valid("ResourceChunkHeader", {**header, "final": "true"}, False)
standalone_valid("游戏消息桥Schema-V0.1.json", {"header": header, "buffer": []}, False)
ack = {**transport, "type": "RESOURCE_ACK", "action": "CONTINUE", "chunkIndex": 0}
standalone_valid("游戏消息桥Schema-V0.1.json", ack, True)
standalone_valid("游戏消息桥Schema-V0.1.json", {**ack, "action": "COMPLETE"}, True)
standalone_valid("游戏消息桥Schema-V0.1.json", {k: v for k, v in ack.items() if k != "chunkIndex"}, False)
standalone_valid("游戏消息桥Schema-V0.1.json", {**transport, "type": "RESOURCE_ACK", "action": "CANCEL"}, True)
standalone_valid("游戏消息桥Schema-V0.1.json", {**ack, "action": "GRANT"}, False)
standalone_valid("游戏消息桥Schema-V0.1.json",
                 {**transport, "type": "RESOURCE_ABORT", "reason": "INTEGRITY_FAILED"}, True)
standalone_valid("游戏消息桥Schema-V0.1.json",
                 {**transport, "type": "RESOURCE_ABORT", "reason": "PAID"}, False)
checks["桥契约边界"] = "保持17个业务RPC；补固定版本资源索引和分块控制形状；不验证实际ArrayBuffer、顺序、ACK背压、摘要或宿主确认"
checks["代表性载荷"] = sample_checks
checks["载荷限制"] = "仅静态结构样本；来源、实际字节、加密、跨字段安全与事务均需实施验证"

for schema_name in ("PaymentCreate", "PaymentAction", "PaymentAttempt"):
    assert "JSAPI" not in json.dumps(schemas[schema_name]), schema_name
assert "READ_RESTORE" not in json.dumps(schemas["SaveWrite"])
assert "JSAPI" not in json.dumps(standalone["游戏消息桥Schema-V0.1.json"])
checks["首期支付与存档动作"] = "PT1机器契约拒绝JSAPI；存档动作移除READ_RESTORE，读取/恢复确认仍由专用接口承担；仅静态拒绝样本"

assert "intentId" in schemas["RunCreate"]["properties"]
assert schemas["RunCreate"]["required"] == ["gameId", "entryMode"]
assert "resumeHandle" not in schemas["PurchaseIntent"]["properties"]
assert "returnAvailable" in schemas["PurchaseIntent"]["properties"]
assert "resume" in schemas["Run"]["properties"]
assert "continue" in schemas["LibraryItem"]["properties"]
assert "INTENT_BINDING_INVALID" in schemas["Error"]["properties"]["code"]["enum"]
assert "intentId" in schemas["Login"]["properties"] and "intentId" not in schemas["Login"]["required"]
login = api["paths"]["/app-api/xj/v1/sessions"]["post"]
create_run = api["paths"]["/app-api/xj/v1/runs"]["post"]
create_order = api["paths"]["/app-api/xj/v1/orders"]["post"]
create_upgrade = api["paths"]["/app-api/xj/v1/upgrades"]["post"]
guest = api["paths"]["/app-api/xj/v1/guest-sessions"]["post"]
bind = api["paths"]["/app-api/xj/v1/purchase-intents/{intentId}/bind"]["post"]
assert all("Set-Cookie" in operation["responses"]["200"]["headers"] for operation in (login, guest))
assert bind["requestBody"]["content"]["application/json"]["schema"]["$ref"] == "#/components/schemas/Empty"
assert "GUEST" in api["paths"]["/app-api/xj/v1/purchase-intents"]["post"]["description"]
assert "PLAYER" in api["paths"]["/app-api/xj/v1/purchase-intents"]["post"]["description"]
quote = api["paths"]["/app-api/xj/v1/quotes"]["post"]
assert "intentId" in schemas["QuoteCreate"]["properties"]
assert "intentId" not in schemas["QuoteCreate"]["required"]
assert "BOUND" in quote["x-authorization"] and "当前会话/账号" in quote["x-authorization"]
assert "24小时" in create_run["description"]
assert "RunCreate.gameId必须等于意图gameId" in create_run["description"]
assert "contentKeys" in create_run["description"]
assert "BOUND原子转为RETURNED" in create_run["description"]
assert "return_run_id" in create_run["description"]
for operation in (create_order, create_upgrade):
    for required_semantic in ("当前PLAYER主体", "expectedAccessRevision == quote.access_revision == 当前权益守卫revision",
                              "在途抵扣", "dueFen=priceFen-creditFen"):
        assert required_semantic in operation["description"], (operation["operationId"], required_semantic)
assert "零补款误走订单" in {case["case"] for case in create_order["x-static-cases"]}
assert "正补款误走升级" in {case["case"] for case in create_upgrade["x-static-cases"]}
for operation in (create_order, create_upgrade):
    assert "revision或报价归属变化拒绝" in {case["case"] for case in operation["x-static-cases"]}
assert "认证成功但guest Cookie或意图不满足交接" in {case["case"] for case in login["x-static-cases"]}
assert "密码账号认证失败才登录失败" in {case["case"] for case in login["x-static-cases"]}
assert {"BOUND首次交付原子转为RETURNED", "RETURNED加return_run_id重放原结果",
        "拒绝作品或意图范围不符", "拒绝换键换run或同键异请求",
        "游客无意图创建与重放"} == {case["case"] for case in create_run["x-static-cases"]}
for required_semantic in ("GUEST/PLAYER会话", "无intentId时为当前会话+gameId+entryMode+适用版本/模式",
                          "同会话同对象同键同请求重放原run"):
    assert required_semantic in create_run["x-idempotency"]
access_doc = (BASE / "03-文档/游戏接入与可信业务链路候选-V0.1.md").read_text()
assert "### 6.1 购买返回契约（RT1已确认）" in access_doc
assert "### 6.2 “我的游戏 / 继续游玩”契约（CL1已确认）" in access_doc
assert "INTENT_BINDING_INVALID" in access_doc and "RunResume.versionId" in access_doc
checks["已确认购买返回与继续契约"] = (
    "RT1：RunCreate.intentId可选、Run.resume受控交付且意图错误稳定拒绝；CL1：LibraryItem.continue只含摘要；"
    "PurchaseIntent不回显handle；仅静态结构检查，跨浏览器/版本/权限语义未运行"
)
checks["GI-A交接静态形状"] = (
    "Login可选单intentId且不接收客户端会话ID，guest/登录声明Set-Cookie，bind空请求，"
    "玩家直接购买路径及报价绑定守卫保留；仅Schema和静态文案检查，未验证Cookie/CSRF/事务/并发"
)
checks["登录运行报价守卫"] = (
    "登录认证与交接失败分离；RunCreate按意图作品/范围校验并声明BOUND→RETURNED及原结果重放；"
    "订单/升级共用报价归属、三重revision、来源/在途抵扣和金额重核；仅静态契约，未运行状态机或事务"
)

model = read("物理数据模型-V0.1.json")
tables = {t["name"]: t for t in model["tables"]}
refs = 0
query_indexes = 0
index_names = set()
for t in tables.values():
    columns = {c["name"]: c for c in t["columns"]}
    assert len(columns) == len(t["columns"])
    for unique in t["unique"]:
        assert all(c in columns for c in unique)
    for index in t.get("queryIndexes", []):
        fields = index["columns"]
        assert fields and len(fields) == len(set(fields))
        assert all(c in columns and columns[c]["sqlType"] not in ("TEXT", "JSON", "MEDIUMBLOB") for c in fields)
        assert not any(key[:len(fields)] == fields for key in t["unique"])
        assert index["name"] not in index_names and len(index["name"]) <= 64
        index_names.add(index["name"])
        query_indexes += 1
    for c in t["columns"]:
        if "references" in c:
            target, col = c["references"].split(".")
            assert any(x["name"] == col for x in tables[target]["columns"])
            assert "ref" in c["key"] and "fk" not in c["key"]
            assert c["referenceKind"] == "logical"
            assert t["store"] == tables[target]["store"]
            refs += 1
        assert "fk" not in c.get("key", [])
assert len(model["stores"]) == 1 and model["stores"][0]["database"] == "xj_play"
assert "xj_rl_operation" not in tables
assert all(t["store"] == "mysql" for t in tables.values())
assert model["physicalForeignKeys"] == []
assert len(model["logicalRelations"]) == refs
assert {(r["from"], r["to"]) for r in model["logicalRelations"]} == {
    (t["name"] + "." + c["name"], c["references"])
    for t in tables.values() for c in t["columns"] if c.get("references")
}
assert ["data_namespace"] in tables["xj_game"]["unique"]
assert ["return_run_id"] in tables["xj_purchase_intent"]["unique"]
intent_fields = {c["name"]: c for c in tables["xj_purchase_intent"]["columns"]}
assert "anonymous_binding" not in intent_fields
assert intent_fields["guest_session_id"]["nullable"] and intent_fields["guest_session_id"]["references"] == "xj_session.id"
assert intent_fields["bound_player_session_id"]["references"] == "xj_session.id"
assert intent_fields["expires_at"]["nullable"]
handoff = tables["xj_intent_handoff"]
assert ["intent_id"] in handoff["unique"]
handoff_fields = {c["name"]: c for c in handoff["columns"]}
assert handoff_fields["intent_id"]["references"] == "xj_purchase_intent.id"
assert handoff_fields["player_session_id"]["references"] == "xj_session.id"
assert handoff_fields["guest_session_id"]["references"] == "xj_session.id"
assert handoff_fields["subject_id"]["references"] == "xj_subject.id"
assert {"expires_at", "consumed_at", "revoked_at", "state"} <= handoff_fields.keys()
checks["GI-A数据结构"] = "匿名/账号意图分流，按意图唯一交接并关联双会话、主体、到期与消费/撤销；仅结构检查，未执行DDL"
assert any(c["name"] == "operation_row_id" and c.get("references") == "xj_restriction_operation.id" for c in tables["xj_rl_event"]["columns"])
analytics = tables["xj_analytics_event"]
assert ["event_key"] in analytics["unique"]
assert ["event_type", "event_key"] not in analytics["unique"]
assert "服务端绑定" in next(c["description"] for c in analytics["columns"] if c["name"] == "event_key")
checks["事件去重规格"] = "服务端按可信作用域派生event_key并单列唯一；不以客户端原编号或event_type组合冒充作用域；仅静态模型检查"
store_ids = {s["id"] for s in model["stores"]}
assert {t["store"] for t in tables.values()} == store_ids
for relation in model["logicalRelations"]:
    source, source_column = relation["from"].split(".")
    target, target_column = relation["to"].split(".")
    assert any(c["name"] == source_column for c in tables[source]["columns"])
    assert any(c["name"] == target_column for c in tables[target]["columns"])
    assert tables[source]["store"] == tables[target]["store"]
checks["物理模型"] = {"tables": len(tables), "columns": sum(len(t["columns"]) for t in tables.values()), "physicalForeignKeys": 0,
                     "logicalRelations": len(model["logicalRelations"]),
                     "stores": {s: sum(t["store"] == s for t in tables.values()) for s in sorted(store_ids)}}
checks["查询索引候选"] = f"{query_indexes}个候选；字段、唯一键冗余与名称静态检查通过；尚未建索引或运行EXPLAIN"
svg = (BASE / "02-图表/完整物理ER-V0.1.svg").read_text()
dot = (BASE / "02-图表/完整物理ER-V0.1.dot").read_text()
assert svg.count('class="node"') == len(tables)
assert svg.count('class="edge"') == refs
assert dot.startswith("digraph XJ {")
assert dot.count(" -> ") == refs
assert "Generated by graphviz version" in svg
mermaid = (BASE / "02-图表/完整物理ER-V0.1.mmd").read_text()
assert not re.search(r"\bFK\b", mermaid)
assert "不建立物理外键" in mermaid
checks["完整ER导出"] = f"Graphviz已实际渲染DOT/SVG；文本与{len(tables)}表、{refs}逻辑关联一致，物理外键0条"
checks["完整ER限制"] = "Graphviz成功渲染不等于全图人工视觉验收通过；非ASCII字宽警告及大画幅审阅限制仍须如实保留。"

manifest_path = BASE / "04-评审/当前资料清单.json"
manifest_ = json.loads(manifest_path.read_text())
for item in manifest_["files"]:
    assert hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"], item["path"]
checks["当前资料指纹"] = f"{len(manifest_['files'])}份当前文件一致；这是整理后快照，不是新业务验收"

documents = [* (ROOT / "docs").rglob("*.md"),
             *(ROOT / name for name in ("README.md", "PRODUCT.md", "DESIGN.md"))]
for file in documents:
    for link in re.findall(r"\]\(([^)]+)\)", file.read_text()):
        target = urlsplit(link.strip("<>"))
        if target.scheme or not target.path:
            continue
        local_path = re.sub(r":\d+(?::\d+)?$", "", unquote(target.path))
        assert (file.parent / local_path).resolve().exists(), (file, link)
checks["本地文档链接"] = "通过"
for repo in ("backend/yudao-boot-mini", "frontend/yudao-ui-admin-vue3"):
    actual = subprocess.check_output(
        ["git", "-C", str(ROOT), "status", "--short", "--", repo], text=True
    )
    assert not actual, (repo, "源码目录有未预期变动")
checks["源码保护"] = "根仓库中的前后端源码目录干净；未读取受保护配置内容或diff"
print(json.dumps({"date": datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat(), "status": "静态契约检查通过；完整ER已渲染，全图视觉验收未完成",
                  "checks": checks}, ensure_ascii=False, indent=2))
