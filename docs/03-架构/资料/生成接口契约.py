"""架构契约生成器；只生成静态规格，不启动HTTP服务或调用支付。"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
S = {}


def text(maximum=128, minimum=1, **kw):
    return {"type": "string", "minLength": minimum, "maxLength": maximum, **kw}


def enum(*values):
    return {"type": "string", "enum": list(values)}


def integer(low=0, high=9007199254740991):
    return {"type": "integer", "minimum": low, "maximum": high}


def array(item, maximum=1000, minimum=0):
    return {"type": "array", "items": item, "minItems": minimum, "maxItems": maximum}


def obj(properties, required=None):
    return {"type": "object", "additionalProperties": False,
            "properties": properties, "required": list(properties) if required is None else required}


def ref(name):
    return {"$ref": "#/components/schemas/" + name}


def schema(name, properties, required=None):
    S[name] = obj(properties, required)
    return ref(name)


ID = text(36, 36, format="uuid")
TIME = text(40, format="date-time")
REV = text(20, pattern="^(0|[1-9][0-9]{0,19})$")
KEY = text(128, pattern="^[A-Za-z0-9._:-]+$")
FORMAT = text(128, pattern="^[!-~]+$")
BOOL = {"type": "boolean"}
MONEY = integer(0, 999999)
EMPTY = schema("Empty", {})
ACK = schema("Acknowledgement", {"operationId": ID, "state": enum("ACCEPTED", "PENDING", "SUCCEEDED", "FAILED")})
schema("Error", {
    "code": enum("AUTH_REQUIRED", "EMAIL_VERIFICATION_REQUIRED", "ACCESS_DENIED",
                 "OBJECT_NOT_AVAILABLE", "VALIDATION_FAILED", "QUOTE_CHANGED", "QUOTE_EXPIRED",
                 "SOURCE_PENDING", "SAVE_CONFLICT", "IDEMPOTENCY_MISMATCH", "SAVE_TOO_LARGE",
                 "PROTOCOL_UNSUPPORTED", "SAVE_INCOMPATIBLE", "ACCOUNT_ACTION_RESTRICTED",
                 "RATE_LIMITED", "GAME_SUSPENDED", "DEPENDENCY_UNAVAILABLE", "REVISION_CHANGED",
                 "INTENT_BINDING_INVALID"),
    "msg": text(1000), "requestId": KEY,
    "data": obj({"operationId": ID, "retryAfterSeconds": integer(), "currentRevision": REV,
                 "field": text(128)}, []),
}, ["code", "msg", "requestId"])
schema("BusinessRef", {"type": enum("order", "grant", "upgrade"), "id": ID})
schema("Account", {"subjectId": ID, "nickname": text(24), "emailVerified": BOOL,
                   "lifecycle": enum("ACTIVE", "DELETION_REQUESTED", "PROCESSING", "DELETED", "EXCEPTION")})
schema("Registration", {"email": text(254, format="email"), "password": text(128, 15), "nickname": text(24)})
schema("Login", {"email": text(254, format="email"), "password": text(128, 15)})
schema("EmailAction", {"email": text(254, format="email")})
schema("TokenAction", {"token": text(512)})
schema("ResetPassword", {"token": text(512), "password": text(128, 15)})
schema("AccountEdit", {"nickname": text(24), "expectedRevision": REV})
schema("EmailChange", {"email": text(254, format="email"), "password": text(128, 15)})
schema("DeletionRequest", {"policyVersion": KEY})
schema("DeletionConfirm", {"expectedRevision": REV, "confirmed": {"const": True}, "token": text(512)})
schema("Deletion", {"id": ID, "state": enum("REQUESTED", "REVIEWING", "AWAIT_CONFIRM", "WITHDRAWN", "PROCESSING", "COMPLETE", "EXCEPTION"),
                    "revision": REV, "blockedBusinessRefs": array(ref("BusinessRef")),
                    "categories": array(obj({"category": KEY, "state": KEY, "nextReviewAt": TIME, "reason": text(1000)}, ["category", "state"]))})
schema("Declarations", {"languages": array(text(32), 20, 1), "devices": array(enum("DESKTOP", "MOBILE"), 2, 1),
                       "contentWarnings": array(text(128), 20), "audio": BOOL, "cloudSave": BOOL})
schema("Product", {"id": ID, "gameId": ID, "kind": enum("BUYOUT", "CHAPTER", "SCENE", "FREE"),
                   "revision": REV, "priceFen": MONEY, "currency": {"const": "CNY"},
                   "promise": text(4000), "contentKeys": array(KEY, 1000, 1),
                   "saleState": enum("DRAFT", "ON_SALE", "DELISTED")})
schema("Game", {"id": ID, "slug": KEY, "title": text(80), "summary": text(160),
                "description": text(2000), "coverResourceId": ID, "screenshotResourceIds": array(ID, 8),
                "declarations": ref("Declarations"), "products": array(ref("Product"), 1000),
                "trialAvailable": BOOL, "publishedAt": TIME, "revision": REV,
                "saleState": enum("DRAFT", "ON_SALE", "DELISTED"),
                "runtimeState": enum("AVAILABLE", "SUSPENDED", "TERMINATING", "CLOSED")})
schema("GameEdit", {"title": text(80), "summary": text(160), "description": text(2000),
                    "coverResourceId": ID, "screenshotResourceIds": array(ID, 8),
                    "declarations": ref("Declarations"), "expectedRevision": REV},
       ["title", "summary", "description", "coverResourceId", "screenshotResourceIds", "declarations"])
schema("RevisionAction", {"expectedRevision": REV, "reason": text(1000)})
schema("Version", {"id": ID, "gameId": ID, "version": KEY, "manifestSha256": text(64, 64, pattern="^[a-f0-9]{64}$"),
                   "packageSha256": text(64, 64, pattern="^[a-f0-9]{64}$"), "revision": REV,
                   "state": enum("UPLOADED", "CHECKING", "REVIEW", "PUBLISHED", "REJECTED", "DISABLED"),
                   "updateNotes": text(1000)})
schema("Publish", {"expectedRevision": REV, "validationReceiptId": ID})
schema("Upload", {"fileName": text(255), "byteSize": integer(1), "sha256": text(64, 64, pattern="^[a-f0-9]{64}$"),
                  "purpose": enum("COVER", "SCREENSHOT", "GAME_PACKAGE")})
schema("UploadPermit", {"uploadId": ID, "uploadUrl": text(2048, format="uri"),
                        "expiresAt": TIME, "maxBytes": integer(1)})
schema("UploadComplete", {"uploadId": ID, "expectedSha256": text(64, 64, pattern="^[a-f0-9]{64}$")})
schema("VersionCreate", {"uploadId": ID, "manifestSha256": text(64, 64, pattern="^[a-f0-9]{64}$"),
                         "updateNotes": text(1000)})
schema("ContentKey", {"id": ID, "gameId": ID, "contentKey": KEY, "meaning": text(1000)})
schema("ContentKeyCreate", {"contentKey": KEY, "meaning": text(1000)})
schema("ProductEdit", {"kind": enum("BUYOUT", "CHAPTER", "SCENE", "FREE"), "priceFen": MONEY,
                       "promise": text(4000), "contentKeys": array(KEY, 1000, 1), "expectedRevision": REV},
       ["kind", "priceFen", "promise", "contentKeys"])
schema("RunCreate", {"gameId": ID, "entryMode": enum("TRIAL", "OWNED", "FREE"), "intentId": ID},
       ["gameId", "entryMode"])
schema("RunResume", {
    "state": enum("AVAILABLE", "UNAVAILABLE"), "handle": text(2048), "versionId": ID,
    "expiresAt": TIME,
    "reason": enum("NO_SAVED_POSITION", "INCOMPATIBLE_VERSION", "EXPIRED", "INTENT_UNAVAILABLE"),
}, ["state"])
S["RunResume"]["allOf"] = [
    {"if": {"properties": {"state": {"const": "AVAILABLE"}}, "required": ["state"]},
     "then": {"required": ["handle", "versionId", "expiresAt"],
              "not": {"required": ["reason"]}}},
    {"if": {"properties": {"state": {"const": "UNAVAILABLE"}}, "required": ["state"]},
     "then": {"required": ["reason"],
              "not": {"anyOf": [{"required": ["handle"]}, {"required": ["versionId"]},
                                {"required": ["expiresAt"]}]}}},
]
schema("RunResource", {
    "path": text(512, pattern="^(?!/)(?!.*(?:^|/)\\.\\.(?:/|$))(?!.*\\\\)[^?#\\x00]+$"),
    "resourceId": ID,
})
schema("Run", {"id": ID, "gameId": ID, "versionId": ID, "mode": enum("TRIAL", "OWNED", "FREE", "PREVIEW"),
               "gameOrigin": text(2048, format="uri"), "entryUrl": text(2048, format="uri"),
               "protocolVersion": {"const": "1.0"}, "capabilities": array(KEY, 20),
               "accessRevision": REV, "expiresAt": TIME, "resourceIndex": array(ref("RunResource"), 10000),
               "resume": ref("RunResume"),
               "subjectPseudonym": text(128), "state": enum("AUTHORIZED", "READY", "EXITED", "FAILED", "REVOKED")},
       ["id", "gameId", "versionId", "mode", "gameOrigin", "entryUrl", "protocolVersion", "capabilities", "accessRevision", "expiresAt", "resourceIndex", "state"])
schema("AccessRequest", {"contentKeys": array(KEY, 1000, 1)})
schema("AccessResult", {"accessRevision": REV, "results": array(obj({
    "contentKey": KEY, "allowed": BOOL, "reason": enum("TRIAL", "GRANTED", "NOT_GRANTED", "SUSPENDED", "UNKNOWN_KEY")}), 1000)})
schema("ResourceRead", {"resourceId": ID})
schema("Ready", {"protocolVersion": {"const": "1.0"}})
schema("Exit", {"reason": enum("USER", "ERROR", "AUTH_EXPIRED", "NAVIGATED")})
schema("PurchaseIntentCreate", {"runId": ID, "contentKeys": array(KEY, 1000, 1), "resumeHandle": text(2048, 0)},
       ["runId", "contentKeys"])
schema("PurchaseIntent", {"id": ID, "gameId": ID, "state": enum("OPEN", "BOUND", "RETURNED", "CANCELLED"),
                          "access": enum("DENIED", "PENDING", "ALLOWED"), "returnAvailable": BOOL,
                          "contentKeys": array(KEY, 1000)})
schema("QuoteCreate", {"productRevisionId": ID, "intentId": ID}, ["productRevisionId"])
schema("CreditSource", {"cashFactId": ID, "netFen": integer(), "allocatedFen": integer(), "revision": REV})
schema("Quote", {"id": ID, "gameId": ID, "productRevisionId": ID, "priceFen": MONEY,
                 "creditFen": MONEY, "dueFen": MONEY, "currency": {"const": "CNY"},
                 "sources": array(ref("CreditSource")), "expiresAt": TIME, "accessRevision": REV})
schema("QuoteConfirm", {"quoteId": ID, "expectedAccessRevision": REV})
schema("Order", {"id": ID, "gameId": ID, "dueFen": MONEY, "currency": {"const": "CNY"},
                 "paymentState": enum("PENDING", "VERIFYING", "PAID", "UNPAID_CLOSED", "EXCEPTION"),
                 "deliveryState": enum("NOT_DUE", "PENDING", "DELIVERED", "EXCEPTION"),
                 "scopeKeys": array(KEY, 1000, 1), "createdAt": TIME, "revision": REV,
                 "supportState": enum("NONE", "OPEN", "CLOSED")})
schema("Upgrade", {
    "id": ID, "gameId": ID, "productRevisionId": ID, "priceFen": MONEY,
    "creditFen": MONEY, "dueFen": MONEY, "currency": {"const": "CNY"},
    "promise": text(4000), "contentKeys": array(KEY, 1000, 1),
    "orderId": ID, "grantId": ID,
    "state": enum("RESERVED", "PENDING", "DELIVERED", "REVIEW", "REVOKED"),
}, ["id", "gameId", "productRevisionId", "priceFen", "creditFen", "dueFen",
    "currency", "promise", "contentKeys", "state"])
S["Upgrade"]["allOf"] = [
    {"if": {"properties": {"state": {"const": "DELIVERED"}}, "required": ["state"]},
     "then": {"required": ["grantId"]}},
    {"if": {"properties": {"dueFen": {"const": 0}}, "required": ["dueFen"]},
     "then": {"not": {"required": ["orderId"]}}},
]
S["Upgrade"]["x-cross-field-validation"] = [
    "productRevisionId、priceFen、promise及contentKeys必须来自同一不可变商品承诺",
    "0<=creditFen<=priceFen且dueFen=priceFen-creditFen；服务端重核，不能采用客户端金额",
    "dueFen=0时orderId为空；dueFen>0时仅在正补款订单由渠道核实并交付后关联",
    "state=DELIVERED时grantId必填；报价内容、金额或访问revision变化均须重新确认",
]
schema("PaymentCreate", {"channel": enum("ALIPAY", "WECHAT"),
                         "method": enum("PAGE", "WAP", "NATIVE", "H5")})
schema("PaymentAction", {"type": enum("FORM", "REDIRECT", "QR"),
                         "expiresAt": TIME, "url": text(2048, format="uri"),
                         "qrText": text(2048), "formHtml": text(12000)},
       ["type", "expiresAt"])
schema("PaymentAttempt", {"id": ID, "orderId": ID, "channel": enum("ALIPAY", "WECHAT"),
                          "method": enum("PAGE", "WAP", "NATIVE", "H5"),
                          "state": enum("CREATING", "WAITING", "UNKNOWN", "SUCCESS", "CLOSED", "FAILED"),
                          "closeState": enum("NONE", "REQUESTED", "CONFIRMED", "UNKNOWN"),
                          "action": ref("PaymentAction")}, ["id", "orderId", "channel", "method", "state", "closeState"])
schema("FreeClaim", {"gameId": ID, "ruleRevision": REV})
schema("Grant", {"id": ID, "gameId": ID, "sourceKind": enum("ORDER", "FREE", "UPGRADE", "COMPENSATION"),
                 "sourceRef": KEY, "state": enum("PENDING", "ACTIVE", "REVIEW", "REVOKED"),
                 "contentKeys": array(KEY), "revision": REV})
schema("ContinueSummary", {
    "available": BOOL, "saveState": enum("NONE", "AVAILABLE", "CONFLICT", "INCOMPATIBLE"),
    "versionId": ID, "lastActivityAt": TIME,
    "accessState": enum("ALLOWED", "DENIED", "PENDING"),
}, ["available", "saveState", "accessState"])
S["ContinueSummary"]["allOf"] = [
    {"if": {"properties": {"available": {"const": True}}, "required": ["available"]},
     "then": {"properties": {"saveState": {"const": "AVAILABLE"}, "accessState": {"const": "ALLOWED"}},
              "required": ["versionId", "lastActivityAt"]}},
]
schema("LibraryItem", {"game": ref("Game"), "grants": array(ref("Grant")),
                       "hasTrialHistory": BOOL, "continue": ref("ContinueSummary")},
       ["game", "grants", "hasTrialHistory"])
schema("SaveMetadata", {"blobId": ID, "format": FORMAT, "byteSize": integer(0, 1048576),
                        "sha256": text(64, 64, pattern="^[a-f0-9]{64}$"), "versionId": ID, "createdAt": TIME})
schema("SaveDescription", {"revision": REV, "current": ref("SaveMetadata"), "previous": ref("SaveMetadata"),
                           "conflict": obj({"id": ID, "left": ref("SaveMetadata"), "right": ref("SaveMetadata")})}, ["revision"])
schema("SaveRead", {"slot": enum("CURRENT", "PREVIOUS", "CONFLICT_LEFT", "CONFLICT_RIGHT"), "expectedRevision": REV})
schema("SavePayload", {"metadata": ref("SaveMetadata"), "revision": REV,
                       "payloadBase64": text(1398104, 0, contentEncoding="base64")})
schema("SaveWrite", {"action": enum("WRITE", "IMPORT", "RESTORE", "RESTART"),
                     "baseRevision": REV, "format": FORMAT, "payloadBase64": text(1398104, 0, contentEncoding="base64"),
                     "sourceBlobId": ID, "conflictId": ID, "confirmed": BOOL},
       ["action", "baseRevision"])
schema("SaveOperation", {"id": ID, "state": enum("ACCEPTED", "PENDING", "SUCCEEDED", "CONFLICT", "FAILED"),
                         "resultRevision": REV, "conflictId": ID}, ["id", "state"])
schema("RestoreConfirm", {"compatible": BOOL, "failureCategory": KEY}, ["compatible"])
schema("SupportCreate", {"businessRef": ref("BusinessRef"),
                         "category": enum("DUPLICATE_PAYMENT", "DELIVERY", "RUNTIME", "VOLUNTARY", "REVOKE", "OTHER"),
                         "description": text(1000)})
schema("Support", {"id": ID, "businessRef": ref("BusinessRef"),
                   "state": enum("ACCEPTED", "REVIEWING", "NEED_INFO", "PROPOSED", "EXECUTING", "CLOSED"),
                   "revision": REV, "nextReviewAt": TIME, "messages": array(obj({
                       "id": ID, "role": enum("PLAYER", "OPERATOR", "SYSTEM"), "text": text(1000), "createdAt": TIME}))})
schema("SupportReply", {"text": text(1000), "expectedRevision": REV})
schema("SupportPlan", {"expectedRevision": REV, "reason": text(1000),
                       "cashRefunds": array(obj({"cashFactId": ID, "amountFen": integer(1)})),
                       "revokeGrantIds": array(ID), "revokeUpgradeIds": array(ID)})
schema("Refund", {"id": ID, "orderId": ID, "cashFactId": ID, "amountFen": integer(1),
                  "cashState": enum("APPROVED", "SENDING", "UNKNOWN", "SUCCEEDED", "FAILED"),
                  "rightsState": enum("PENDING", "ADJUSTED", "EXCEPTION"), "revision": REV})
schema("Report", {"metric": enum(*[f"M-{i:02}" for i in range(1, 12)]), "periodStart": TIME,
                  "periodEnd": TIME, "asOf": TIME, "definitionVersion": KEY,
                  "currency": {"const": "CNY"}, "success": integer(), "failed": integer(),
                  "unknown": integer(), "cancelled": integer(), "sampleCount": integer(),
                  "amountFen": integer(-9007199254740991), "feeState": enum("UNKNOWN", "VERIFIED", "PARTIAL"),
                  "coverage": text(1000)},
       ["metric", "periodStart", "periodEnd", "asOf", "definitionVersion", "currency", "success", "failed", "unknown", "cancelled", "sampleCount", "feeState", "coverage"])
schema("Job", {"id": ID, "state": enum("READY", "LEASED", "DONE", "RETRY", "DEAD"),
               "businessRef": text(128), "nextAttemptAt": TIME, "attempts": integer(), "revision": REV})
schema("Audit", {"id": ID, "operatorRef": KEY, "action": KEY, "businessRef": text(128),
                 "result": KEY, "createdAt": TIME, "traceId": KEY})

# Action-dependent payloads are executable schema constraints, not only prose.
S["SaveWrite"]["allOf"] = [
    {"if": {"properties": {"action": {"enum": ["WRITE", "IMPORT"]}}, "required": ["action"]},
     "then": {"required": ["format", "payloadBase64"]}},
    {"if": {"properties": {"action": {"const": "RESTORE"}}, "required": ["action"]},
     "then": {"required": ["sourceBlobId"]}},
    {"if": {"properties": {"action": {"enum": ["IMPORT", "RESTORE", "RESTART"]}}, "required": ["action"]},
     "then": {"required": ["confirmed"], "properties": {"confirmed": {"const": True}}}},
]
S["PaymentCreate"]["oneOf"] = [
    {"properties": {"channel": {"const": "ALIPAY"}, "method": {"enum": ["PAGE", "WAP"]}}},
    {"properties": {"channel": {"const": "WECHAT"}, "method": {"enum": ["NATIVE", "H5"]}}},
]
S["PaymentAction"]["allOf"] = [
    {"if": {"properties": {"type": {"const": t}}},
     "then": {"required": [field]}}
    for t, field in [("FORM", "formHtml"), ("REDIRECT", "url"), ("QR", "qrText")]
]
for product in ("Product", "ProductEdit"):
    S[product]["allOf"] = [
        {"if": {"properties": {"kind": {"const": "FREE"}}, "required": ["kind"]},
         "then": {"properties": {"priceFen": {"const": 0}}},
         "else": {"properties": {"priceFen": integer(1, 999999)}}}
    ]

# Events share product spelling; source trust is an explicit part of each variant.
event_rows = """
game_detail_expose|WEB|game_ref,view_ref
game_launch_authorize_success|SERVER|run_ref,entry_mode
game_trial_success|GAME|run_ref,entry_mode
order_payment_click|SERVER|order_ref
order_payment_success|SERVER|order_ref,payment_ref
order_payment_fail|SERVER|order_ref,failure_category
entitlement_delivery_success|SERVER|scope_ref
entitlement_delivery_fail|SERVER|order_ref,failure_category
game_launch_success|GAME|run_ref,entry_mode
game_launch_fail|GAME|run_ref,failure_category
game_access_fail|SERVER|failure_category
save_write_success|SERVER|save_revision,operation_ref
save_write_accept_success|SERVER|operation_ref
save_write_fail|SERVER|failure_category,operation_ref
save_restore_success|GAME|save_revision,operation_ref
save_restore_accept_success|SERVER|operation_ref
save_restore_fail|GAME|failure_category,operation_ref
game_release_success|SERVER|version_ref,release_attempt_ref
game_release_accept_success|SERVER|release_attempt_ref,version_ref
game_release_fail|SERVER|version_ref,failure_category,release_attempt_ref
support_request_success|SERVER|businessRef
order_refund_success|SERVER|refund_ref,order_ref
order_refund_fail|SERVER|refund_ref,order_ref,failure_category
account_action_accept_success|SERVER|operation_ref,action_type
account_action_success|SERVER|operation_ref,action_type
account_action_fail|SERVER|operation_ref,action_type,failure_category
order_create_success|SERVER|order_ref,scope_ref
free_claim_accept_success|SERVER|operation_ref,game_ref
free_claim_success|SERVER|operation_ref,scope_ref
free_claim_fail|SERVER|operation_ref,failure_category
game_upgrade_success|SERVER|upgrade_ref,scope_ref
""".strip()
events = []
for line in event_rows.splitlines():
    name, source, fields = line.split("|")
    required = fields.split(",")
    props = {f: (ref("BusinessRef") if f == "businessRef" else KEY) for f in required}
    if name == "game_detail_expose":
        props["source"] = text(128)
    if name == "support_request_success":
        props.update(order_ref=KEY, refund_ref=KEY)
    if name == "entitlement_delivery_success":
        props["order_ref"] = KEY
    if name == "save_restore_fail":
        props["save_revision"] = REV
    if name == "game_access_fail":
        props["scope_ref"] = KEY
    if "entry_mode" in props:
        props["entry_mode"] = enum("TRIAL", "FREE", "OWNED", "PREVIEW")
    if "action_type" in props:
        props["action_type"] = enum("register", "verify", "reset", "delete", "change_email")
    variant = obj({
        "event_ref": {**KEY, "description": "原事件实例编号；同次重试保持编号及载荷；不是数据库全局唯一键或可信付款证明"},
        "type": {"const": name}, "occurred_at": TIME,
        "game_ref": ID, "version_ref": ID, "run_ref": ID,
        "account_ref": KEY, "fields": obj(props, required),
    }, ["event_ref", "type", "occurred_at", "fields"])
    # All runtime identity is canonicalized from run; schema cannot prove origin or truth.
    if source == "GAME":
        variant["required"] += ["game_ref", "version_ref", "run_ref"]
    variant["x-trusted-source"] = source
    variant["x-server-canonicalization"] = "归属/模式/来源由服务端核定；event_key按环境和可信作用域派生，GAME绑定run、WEB绑定平台会话及作品、SERVER绑定持久事件；同键异载荷拒绝，详见数据与运营6.1；游戏结果不证明现金或权益"
    S["Event_" + name] = variant
    events.append((name, source))
S["Event"] = {"oneOf": [ref("Event_" + n) for n, _ in events]}
S["GameEvent"] = {"oneOf": [ref("Event_" + n) for n, source in events if source == "GAME"]}
schema("GameEvents", {"events": array(ref("GameEvent"), 20, 1)})
schema("WebEvents", {"events": array(ref("Event_game_detail_expose"), 20, 1)})
schema("EventReceipt", {"accepted": array(KEY, 20), "duplicates": array(KEY, 20),
                        "rejected": array(obj({"eventRef": KEY, "code": KEY}), 20)})

paths = {}
APP = "/app-api/xj/v1"
ADMIN = "/admin-api/xj/v1"
errors = {"400": "参数/CSRF校验失败", "401": "会话缺失或失效", "403": "验证、权限或归属拒绝",
          "404": "不可见或不存在", "409": "修订、报价或幂等冲突", "413": "请求/存档超限",
          "422": "协议或格式不兼容", "423": "账号生命周期限制", "429": "限流", "503": "依赖或游戏不可用"}


def page(name):
    name_ = name + "Page"
    if name_ not in S:
        schema(name_, {"items": array(ref(name), 100),
                       "pageNo": integer(1), "effectivePageNo": integer(1),
                       "pageSize": integer(1, 100), "total": integer()})
    return name_


def operation(prefix, path, method, name, title, output="Acknowledgement",
              request=None, auth="player", permission=None, paged=False, params=(),
              notes="", status="200", accepted=False):
    params = list(params)
    for token in path.split("/"):
        if token.startswith("{"):
            params.append({"name": token[1:-1], "in": "path", "required": True, "schema": ID})
    if paged:
        output = page(output)
        params += [{"name": "pageNo", "in": "query", "schema": integer(1)},
                   {"name": "pageSize", "in": "query",
                    "schema": {"const": 12} if prefix == APP else integer(1, 100)}]
    if method != "get":
        params.append({"name": "Idempotency-Key", "in": "header", "required": True, "schema": KEY})
        if auth != "admin":
            params.append({"name": "X-CSRF-Token", "in": "header", "required": True, "schema": text(256)})
    response_schema = obj({"code": {"const": 0}, "msg": text(1000, 0),
                           "requestId": KEY, "data": ref(output)})
    responses = {status: {"description": title + "的可信结果",
                          "content": {"application/json": {"schema": response_schema}},
                          "headers": {"Cache-Control": {"schema": {"const": "no-store"}, "description": "私人接口不缓存"}}}}
    for code, desc in errors.items():
        responses[code] = {"description": desc, "content": {"application/json": {"schema": ref("Error")}}}
    if accepted:
        responses["202"] = {"description": "已受理但未完成；按返回业务对象id使用本接口明示的查询路径，结果结构与200一致",
                            "content": {"application/json": {"schema": response_schema}}}
    op = {"operationId": name, "summary": title, "description": notes or title,
          "tags": ["后台" if prefix == ADMIN else "玩家"],
          "parameters": params, "responses": responses,
          "security": ([{"adminBearer": []}] if auth == "admin" else [{"playerSession": []}]),
          "x-authorization": permission or ("公开；不泄露私人对象" if auth == "public" else
                             "验证当前主体与对象归属；新增资产/私人云档另需邮箱已验证"),
          "x-version-policy": "v1重大不兼容变更新major；兼容窗口另定",
          "x-idempotency": "可信主体+动作+对象+key；同key不同payload=409；重试复用key；持久唯一关系兜底",
          "x-runtime-status": "仅设计，尚未实施"}
    if auth == "public":
        op["security"] = []
    if auth == "guest":
        op["x-authorization"] = "平台受控匿名或玩家会话；每次验证run/版本/会话归属；游客仅试玩"
    if request:
        op["requestBody"] = {"required": True, "content": {"application/json": {"schema": ref(request)}}}
    paths.setdefault(prefix + path, {})[method] = op


def query(name, sch):
    return {"name": name, "in": "query", "schema": sch}


operation(APP, "/session", "get", "getSession", "查询当前账号", "Account")
operation(APP, "/guest-sessions", "post", "createGuestSession", "签发匿名试玩会话", auth="public",
          notes="Origin/CSRF引导校验和限流；只签发HttpOnly匿名Cookie，无账号资产", output="RunSession")
schema("RunSession", {"mode": enum("GUEST"), "expiresAt": TIME})
operation(APP, "/csrf", "get", "getCsrfToken", "取得宿主CSRF引导令牌", "Csrf", auth="public")
schema("Csrf", {"token": text(256)})
for path_, name, body, title in [
    ("/accounts", "registerAccount", "Registration", "注册受理"),
    ("/sessions", "loginPlayer", "Login", "玩家登录"),
    ("/email-verifications", "sendVerification", "EmailAction", "发送验证邮件"),
    ("/email-verifications/complete", "completeVerification", "TokenAction", "完成邮箱验证"),
    ("/password-resets", "requestReset", "EmailAction", "找回口令受理"),
    ("/password-resets/complete", "completeReset", "ResetPassword", "重置口令并撤销旧会话"),
]:
    operation(APP, path_, "post", name, title, request=body, auth="public",
              notes="泛化存在性反馈；成功重发才切换旧令牌；60秒/小时5次；token不进URL日志")
operation(APP, "/sessions/current/logout", "post", "logoutPlayer", "退出并撤销当前会话", request="Empty")
operation(APP, "/account/profile", "patch", "editProfile", "更新玩家昵称", "Account", "AccountEdit")
operation(APP, "/account/email-change", "post", "changeEmail", "请求变更邮箱", request="EmailChange")
operation(APP, "/account/deletion", "post", "requestDeletion", "申请分类注销", "Deletion", "DeletionRequest")
operation(APP, "/account/deletion", "get", "getDeletion", "查询注销分类状态", "Deletion")
operation(APP, "/account/deletion/confirm", "post", "confirmDeletion", "最终确认注销并立刻撤会话", "Deletion", "DeletionConfirm")
operation(APP, "/account/deletion/withdraw", "post", "withdrawDeletion", "最终确认前撤回注销", "Deletion", "RevisionAction")
operation(APP, "/games", "get", "listGames", "发现与筛选已公开作品", "Game", auth="public", paged=True,
          params=[query("keyword", text(100, 0)), query("mode", enum("ALL", "FREE", "BUYOUT", "CHAPTER", "SCENE")),
                  query("device", enum("DESKTOP", "MOBILE")), query("sort", enum("PUBLISHED_DESC"))])
operation(APP, "/games/{gameId}", "get", "getGame", "查询公开作品详情", "Game", auth="public")
operation(APP, "/web-events", "post", "reportWebEvents", "记录详情观察事件", "EventReceipt", "WebEvents", auth="public")
operation(APP, "/runs", "post", "createRun", "核实范围后创建运行", "Run", "RunCreate", auth="guest")
operation(APP, "/runs/{runId}/context", "get", "getRunContext", "取得最小运行上下文", "Run", auth="guest")
operation(APP, "/runs/{runId}/access/check", "post", "checkAccess", "核对当前内容权限", "AccessResult", "AccessRequest", auth="guest")
operation(APP, "/runs/{runId}/resources/read", "post", "readResource", "读取已发布且当前获准资源", "Empty", "ResourceRead", auth="guest",
          notes="由宿主代调；当前会话/run/版本/内容全检查；拒绝任意URL；Content-Type按已审核MIME；nosniff/no-store")
paths[APP + "/runs/{runId}/resources/read"]["post"]["responses"]["200"] = {
    "description": "受控二进制；审核MIME、nosniff、no-store；游戏经MessagePort接收ArrayBuffer",
    "content": {"application/octet-stream": {"schema": {"type": "string", "contentEncoding": "binary"}}},
    "headers": {"Content-Type": {"schema": text(128)}, "Cache-Control": {"schema": {"const": "no-store"}},
                "X-Content-Type-Options": {"schema": {"const": "nosniff"}},
                "X-Resource-SHA256": {"schema": text(64, 64)}}}
operation(APP, "/runs/{runId}/ready", "post", "readyRun", "声明已可交互并核验运行", "Run", "Ready", auth="guest")
operation(APP, "/runs/{runId}/exit", "post", "exitRun", "关闭当前运行桥", request="Exit", auth="guest")
operation(APP, "/purchase-intents", "post", "createIntent", "登记原游戏购买返回意图", "PurchaseIntent", "PurchaseIntentCreate", auth="guest")
operation(APP, "/purchase-intents/{intentId}/bind", "post", "bindIntent", "登录后核验并承接匿名意图", "PurchaseIntent", "Empty",
          notes="必须核验原匿名绑定与新登录会话；仅持intentId不足以认领")
operation(APP, "/purchase-intents/{intentId}", "get", "getIntent", "查询购买返回及当前访问状态", "PurchaseIntent", auth="guest")
operation(APP, "/quotes", "post", "createQuote", "生成10分钟服务端报价", "Quote", "QuoteCreate")
operation(APP, "/orders", "post", "createOrder", "重核报价并创建正应付订单", "Order", "QuoteConfirm",
          notes="dueFen必须>0；不接受客户端金额；零补款返回409并引导独立upgrade操作")
operation(APP, "/upgrades", "post", "createUpgrade", "重核并创建零补款升级", "Upgrade", "QuoteConfirm",
          notes="该入口只接dueFen=0；不制造支付订单；正补款订单核实交付后关联升级")
operation(APP, "/orders", "get", "listOrders", "查询本人订单", "Order", paged=True)
operation(APP, "/orders/{orderId}", "get", "getOrder", "分开查询付款交付售后状态", "Order")
operation(APP, "/orders/{orderId}/payment-attempts", "post", "createPayment", "选择支付宝或微信付款尝试", "PaymentAttempt", "PaymentCreate",
          notes="首期仅接受支付宝PAGE/WAP与微信NATIVE/H5；JSAPI及小程序不在首期；服务端验证浏览器/商户产品资格、可支付状态与渠道切换守卫；旧尝试UNKNOWN先核实，不靠新out_trade_no重试")
operation(APP, "/payment-attempts/{attemptId}", "get", "getPayment", "查询本人付款尝试", "PaymentAttempt")
operation(APP, "/payment-attempts/{attemptId}/reconcile", "post", "reconcilePayment", "请求有界可信查单", "PaymentAttempt", "Empty")
operation(APP, "/orders/{orderId}/close", "post", "closeOrder", "请求关单并等待渠道核实", "Order", "RevisionAction")
operation(APP, "/claims/free", "post", "claimFree", "已验证账号免费领取", "Grant", "FreeClaim")
operation(APP, "/library", "get", "getLibrary", "分别返回授予与试玩记录", "LibraryItem", paged=True)
operation(APP, "/upgrades/{upgradeId}", "get", "getUpgrade", "查询本人差价升级", "Upgrade")
operation(APP, "/runs/{runId}/save", "get", "describeSave", "查询当前档恢复点及冲突", "SaveDescription")
operation(APP, "/runs/{runId}/save/read", "post", "readSave", "受控读取选定存档来源", "SavePayload", "SaveRead")
operation(APP, "/runs/{runId}/save-operations", "post", "operateSave", "提交CAS保存导入恢复重开", "SaveOperation", "SaveWrite",
          notes="WRITE/IMPORT需format+payload，RESTORE需sourceBlobId，RESTART/IMPORT/RESTORE需confirmed=true；读取来源走save/read，兼容确认走restore-confirm，不以READ_RESTORE动作冒充恢复；此值仅为宿主确认后的意图，不是授权证明；宿主确认绑定当前主体/run/action/baseRevision及payload摘要或sourceBlobId；服务端仍验证归属/CAS/幂等；编码后未压缩<=1048576字节；第三冲突源拒收并留来源端；202仍返回SaveOperation，按id查询GET /save-operations/{operationId}",
          accepted=True)
operation(APP, "/save-operations/{operationId}", "get", "getSaveOperation", "查同次保存操作结果", "SaveOperation")
operation(APP, "/save-operations/{operationId}/restore-confirm", "post", "confirmRestore", "游戏报告兼容恢复结果", "SaveOperation", "RestoreConfirm",
          notes="宿主核对本run/操作/来源；游戏报告仅解释存档兼容，不赋予权益")
operation(APP, "/runs/{runId}/events", "post", "reportGameEvents", "接收游戏来源白名单事件", "EventReceipt", "GameEvents", auth="guest")
operation(APP, "/support-cases", "post", "createSupport", "登记订单授予或升级售后", "Support", "SupportCreate")
operation(APP, "/support-cases", "get", "listSupport", "查询本人售后", "Support", paged=True)
operation(APP, "/support-cases/{supportId}", "get", "getSupport", "查询本人售后进度", "Support")
operation(APP, "/support-cases/{supportId}/messages", "post", "replySupport", "补充售后说明", "Support", "SupportReply")

# Admin bearer retains system authentication, with new explicit object-scope permissions.
admin_rows = [
    ("/games", "get", "adminListGames", "作品管理列表", "Game", None, "game:read", True),
    ("/games", "post", "adminCreateGame", "新建作品草稿", "Game", "GameEdit", "game:write", False),
    ("/games/{gameId}", "patch", "adminEditGame", "修订作品展示资料", "Game", "GameEdit", "game:write", False),
    ("/games/{gameId}/state", "post", "adminChangeGameState", "停售暂停或终止服务", "Game", "GameStateChange", "game:operate", False),
    ("/uploads", "post", "adminRequestUpload", "申请受限资源上传", "UploadPermit", "Upload", "release:upload", False),
    ("/uploads/complete", "post", "adminCompleteUpload", "核对真实对象摘要及扫描", "Acknowledgement", "UploadComplete", "release:upload", False),
    ("/games/{gameId}/versions", "post", "adminCreateVersion", "登记不可变版本", "Version", "VersionCreate", "release:write", False),
    ("/games/{gameId}/versions", "get", "adminListVersions", "查询作品版本", "Version", None, "release:read", True),
    ("/game-versions/{versionId}/validate", "post", "adminValidateVersion", "接入包验证受理", "Acknowledgement", "RevisionAction", "release:review", False),
    ("/game-versions/{versionId}/preview", "post", "adminPreviewVersion", "签发受限预览运行", "Run", "RevisionAction", "release:preview", False),
    ("/game-versions/{versionId}/publish", "post", "adminPublishVersion", "校验后发布指定版本", "Acknowledgement", "Publish", "release:publish", False),
    ("/games/{gameId}/content-keys", "post", "adminCreateContent", "登记稳定内容含义", "ContentKey", "ContentKeyCreate", "catalog:write", False),
    ("/games/{gameId}/products", "get", "adminListProducts", "查询商品承诺版本", "Product", None, "catalog:read", True),
    ("/games/{gameId}/products", "post", "adminCreateProduct", "新建不可变商品承诺", "Product", "ProductEdit", "catalog:write", False),
    ("/products/{productId}/state", "post", "adminProductState", "变更商品售卖状态", "Product", "ProductStateChange", "catalog:operate", False),
    ("/orders", "get", "adminListOrders", "受限查询订单", "Order", None, "trade:read", True),
    ("/orders/{orderId}", "get", "adminGetOrder", "核对付款交付与售后", "Order", None, "trade:read", False),
    ("/orders/{orderId}/reconcile", "post", "adminReconcileOrder", "受控查证所有支付尝试", "Acknowledgement", "RevisionAction", "trade:reconcile", False),
    ("/support-cases", "get", "adminListSupport", "查询售后与超时队列", "Support", None, "support:read", True),
    ("/support-cases/{supportId}/messages", "post", "adminReplySupport", "人工更新处理记录", "Support", "SupportReply", "support:write", False),
    ("/support-cases/{supportId}/plan", "post", "adminProposePlan", "记录现金与来源处置方案", "Support", "SupportPlan", "support:approve", False),
    ("/support-cases/{supportId}/execute", "post", "adminExecutePlan", "执行已批准售后方案", "Acknowledgement", "RevisionAction", "support:execute", False),
    ("/refunds", "get", "adminListRefunds", "查询现金与撤权分别状态", "Refund", None, "refund:read", True),
    ("/refunds/{refundId}/execute", "post", "adminExecuteRefund", "执行原路退款并保留额度", "Refund", "RevisionAction", "refund:execute", False),
    ("/refunds/{refundId}/reconcile", "post", "adminReconcileRefund", "查证原退款号", "Refund", "RevisionAction", "refund:reconcile", False),
    ("/reports", "get", "adminReports", "区间指标及可信现金核对", "Report", None, "report:read", False),
    ("/jobs", "get", "adminListJobs", "查看补偿清理与发布任务", "Job", None, "operations:read", True),
    ("/jobs/{jobId}/retry", "post", "adminRetryJob", "重试同业务任务", "Job", "RevisionAction", "operations:retry", False),
    ("/audit-events", "get", "adminAudit", "最小必要审计查询", "Audit", None, "audit:read", True),
]
schema("GameStateChange", {"expectedRevision": REV, "saleState": enum("DRAFT", "ON_SALE", "DELISTED"),
                           "runtimeState": enum("AVAILABLE", "SUSPENDED", "TERMINATING", "CLOSED"),
                           "reason": text(1000), "servicePlanRef": ID}, ["expectedRevision", "reason"])
schema("ProductStateChange", {"expectedRevision": REV, "saleState": enum("ON_SALE", "DELISTED"), "reason": text(1000)})
for p, method, name, title, output, request, permission, paged in admin_rows:
    operation(ADMIN, p, method, name, title, output, request, auth="admin", permission="xj:" + permission + " + 服务端作品/对象作用域", paged=paged)
paths[ADMIN + "/reports"]["get"]["parameters"] += [
    query("metric", S["Report"]["properties"]["metric"]), query("start", TIME), query("end", TIME),
    query("asOf", TIME), query("gameId", ID), query("currency", {"const": "CNY"})]
paths[ADMIN + "/reports"]["get"]["description"] = "区间左闭右开，Asia/Shanghai；1–366日；asOf修订；30日外明细不凭空恢复，覆盖不足如实标注"

paths[APP + "/runs"]["post"]["description"] += (
    "；可选intentId只接受公开意图编号，服务端核对当前会话、匿名绑定、作品、当前访问和版本后，"
    "才通过Run.resume交付受控位置；不存在或不属于当前绑定返回INTENT_BINDING_INVALID。"
    "RunResume.versionId必须等于本次Run.versionId，位置不授权、不跨版本静默复用、不写URL或日志。"
)
paths[APP + "/purchase-intents/{intentId}"]["get"]["description"] += (
    "；只返回绑定、状态、当前访问及returnAvailable，不回显resumeHandle或可直接恢复的位置。"
)
paths[APP + "/library"]["get"]["description"] += (
    "；continue仅返回可用性、保存状态、适用版本、最近活动及访问状态，不返回payload、剧情文本、"
    "资源路径或原始handle；摘要不证明读档成功或授予权益。"
)
paths[APP + "/upgrades"]["post"]["description"] += (
    "；Upgrade必须完整返回目标productRevisionId、priceFen、currency、promise与contentKeys，"
    "以及服务端重核的creditFen/dueFen；零补款不得返回orderId，交付时必须返回grantId。"
)

restriction_operations = {
    "logoutPlayer", "completeReset", "requestDeletion", "confirmDeletion",
    "adminChangeGameState", "adminExecutePlan",
}
for item in paths.values():
    for op in item.values():
        if op["operationId"] not in restriction_operations:
            continue
        op["x-restriction-completion"] = "SD2：涉及限制时，业务限制/操作/事件/头/必要outbox同一事务提交后才报告该限制完成"
        op["description"] += (
            "；涉及注销、撤会话、撤权或暂停时按SD2使用xj_play同库事务。"
            "对应限制变更及APPLIED操作/事件/头/必要outbox须同一事务提交；"
            "不再使用独立PREPARED或跨库补写。提交未明返回503，"
            "按原Idempotency-Key查证/重试，不换键另做；旧快照缺行不能证明未执行。"
            "业务对象仍按自身state表达，注销PROCESSING或售后受理"
            "不等于游戏分类清理、现金退款或权益调整全部完成。"
        )
        op["responses"]["503"]["description"] += "；限制提交可能未明，不能推断未执行，复用原键查证"
        if op["operationId"] == "completeReset":
            op["description"] += (
                "；重置的一次性令牌消费、口令更新、会话撤销与限制记录同一本地事务提交。"
                "重试先以原动作、原键及可信请求绑定核对原持久结果，"
                "不能仅因原令牌已消费而丢失已成功结果，也不能只凭请求键读取他人结果；"
                "限制计划、事件与日志不得包含口令、原始令牌或密码哈希。"
            )

# Native notification surfaces preserve channel-specific acknowledgement; no Cookie/CSRF wrapper.
schema("AlipayNotice", {
    "notify_time": text(64), "notify_type": text(64), "notify_id": text(128),
    "app_id": text(128), "charset": text(32), "version": text(32),
    "sign_type": enum("RSA2"), "sign": text(2048), "out_trade_no": text(64),
    "trade_no": text(128), "trade_status": enum("WAIT_BUYER_PAY", "TRADE_CLOSED", "TRADE_SUCCESS", "TRADE_FINISHED"),
    "total_amount": text(32, pattern="^[0-9]+\\.[0-9]{2}$"), "seller_id": text(128),
}, ["app_id", "sign_type", "sign", "out_trade_no", "trade_no", "trade_status", "total_amount", "seller_id"])
# Channel additions are allowed only here, kept in original verification input then explicitly projected.
S["AlipayNotice"]["additionalProperties"] = {"type": "string"}
schema("WechatNotice", {"id": text(128), "create_time": TIME, "event_type": text(128),
                        "resource_type": text(128), "summary": text(1000),
                        "resource": obj({"algorithm": {"const": "AEAD_AES_256_GCM"}, "ciphertext": text(1048576),
                                         "associated_data": text(1024, 0), "nonce": text(128),
                                         "original_type": text(128)}, ["algorithm", "ciphertext", "nonce"])})
for channel in ("alipay", "wechat"):
    for kind in ("payments", "refunds") if channel == "wechat" else ("payments",):
        notice_name = "AlipayNotice" if channel == "alipay" else "WechatNotice"
        media = "application/x-www-form-urlencoded" if channel == "alipay" else "application/json"
        success = {"type": "string", "const": "success"} if channel == "alipay" else EMPTY
        op = {
            "operationId": channel + kind.title() + "Notify", "summary": f"{channel} {kind}原生通知",
            "security": [], "tags": ["渠道通知"],
            "description": "保留原始请求验签；校验商户/应用/原订单/金额/币种/状态；落盘去重与可靠后续任务后才确认。未知或存储故障按渠道失败应答并查证",
            "parameters": [] if channel == "alipay" else [
                {"name": h, "in": "header", "required": True, "schema": text(4096)}
                for h in ("Wechatpay-Serial", "Wechatpay-Signature", "Wechatpay-Timestamp", "Wechatpay-Nonce")],
            "requestBody": {"required": True, "content": {media: {"schema": ref(notice_name)}}},
            "responses": {
                "200" if channel == "alipay" else "204": {
                    "description": "渠道原生成功应答；微信204无正文",
                    **({"content": {"text/plain": {"schema": success}}} if channel == "alipay" else {})},
                "400": {"description": "签名/数据校验拒绝；按渠道失败协议"},
                "500": {"description": "持久处理失败；不确认成功，等待重试并查单"}},
            "x-authentication": "CHANNEL_SIGNATURE；独立于玩家/管理员会话",
            "x-runtime-status": "设计，原生字段以官方适配资料核定",
        }
        if channel == "alipay":
            op["responses"]["200"]["description"] += "；拒绝或处理失败不得输出success，可按官方返回failure"
        paths.setdefault(f"/app-api/xj/v1/{kind}/notifications/{channel}", {})["post"] = op

document = {
    "openapi": "3.1.1",
    "info": {"title": "间隙PLAY 平台接口架构草案", "version": "0.1.0",
             "description": "2026-10-25。设计规格，未运行。覆盖玩家/平台后台/双支付通知；既有system/infra独立保留，不冒称已完成对接。"},
    "servers": [{"url": "https://platform.invalid", "description": "文档占位，非已部署域名"}],
    "paths": paths,
    "components": {
        "securitySchemes": {
            "playerSession": {"type": "apiKey", "in": "cookie", "name": "__Host-xj-session",
                              "description": "宿主HttpOnly/Secure/SameSite，玩家与匿名由服务端区分；每次校验撤销代次"},
            "adminBearer": {"type": "http", "scheme": "bearer",
                            "description": "适配既有system，token不意味着已具对象权限；不承诺JWT"},
        },
        "schemas": S,
    },
    "x-limits-status": "事件单批20/资源上传配额/包大小为架构建议或待资源核准；不改变已确认产品每页12与存档1MiB",
}
(BASE / "资料/平台OpenAPI-V0.1.json").write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
# Standalone JSON Schema document rewrites local component references.
event_doc = {"$schema": "https://json-schema.org/draft/2020-12/schema",
             "$id": "https://schema.invalid/xj/events/1.0", "title": "固定31事件及可信来源",
             "$defs": {name: value for name, value in S.items() if name.startswith("Event") or name == "BusinessRef"},
             "$ref": "#/$defs/Event"}
raw = json.dumps(event_doc, ensure_ascii=False, indent=2).replace("#/components/schemas/", "#/$defs/")
(BASE / "资料/平台事件Schema-V0.1.json").write_text(raw + "\n")
print(f"已生成OpenAPI设计：{sum(len(v) for v in paths.values())}个操作/{len(S)}个schema，固定{len(events)}事件")
