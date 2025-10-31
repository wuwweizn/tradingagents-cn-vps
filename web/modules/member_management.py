import json
import time
from pathlib import Path
import streamlit as st

# 认证与日志
try:
    from web.utils.auth_manager import auth_manager
except Exception:
    from ..utils.auth_manager import auth_manager  # type: ignore


USERS_FILE = Path(__file__).parent.parent / "config" / "users.json"


def _load_users() -> dict:
	try:
		if USERS_FILE.exists():
			return json.loads(USERS_FILE.read_text(encoding="utf-8"))
		return {}
	except Exception as e:
		st.error(f"❌ 读取用户数据失败: {e}")
		return {}


def _save_users(users: dict) -> bool:
	try:
		USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
		USERS_FILE.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")
		return True
	except Exception as e:
		st.error(f"❌ 保存用户数据失败: {e}")
		return False


def _ensure_admin_self_protection(target_username: str) -> None:
	current = auth_manager.get_current_user() if auth_manager else None
	if current and current.get("username") == target_username:
		st.warning("⚠️ 不允许对当前登录管理员账户执行该高危操作")
		st.stop()


def _render_users_table(users: dict) -> None:
	rows = []
	for username, info in users.items():
		rows.append({
			"用户名": username,
			"角色": info.get("role", "user"),
			"权限": ", ".join(info.get("permissions", [])),
			"点数": int(info.get("points", 0)),
			"创建时间": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info.get("created_at", time.time())))
		})
	if rows:
		st.dataframe(rows, use_container_width=True)
	else:
		st.info("暂无用户数据")


def _create_user_form(users: dict) -> None:
	st.subheader("➕ 新增会员")
	with st.form("create_user_form", clear_on_submit=True):
		col1, col2 = st.columns(2)
		with col1:
			username = st.text_input("用户名", placeholder="例如: user01")
			role = st.selectbox("角色", ["user", "admin"], index=0)
		with col2:
			password = st.text_input("初始密码", type="password", placeholder="建议强密码")
			perms = st.multiselect("权限", ["analysis", "batch_analysis", "config", "admin"], default=["analysis"]) 
			points = st.number_input("初始点数", min_value=0, value=10, step=1)
		submitted = st.form_submit_button("创建")
		if submitted:
			if not username or not password:
				st.error("用户名和密码不能为空")
				return
			if username in users:
				st.error("该用户名已存在")
				return
			# 使用 AuthManager 的哈希规则保持一致
			from web.utils.auth_manager import AuthManager
			hasher = AuthManager()
			users[username] = {
				"password_hash": hasher._hash_password(password),
				"role": role,
				"permissions": perms,
				"points": int(points),
				"created_at": time.time()
			}
			if _save_users(users):
				st.success("✅ 创建成功")
				st.experimental_rerun()


def _update_user_form(users: dict) -> None:
	st.subheader("✏️ 编辑会员")
	usernames = list(users.keys())
	if not usernames:
		st.info("暂无用户可编辑")
		return
	selected = st.selectbox("选择用户", usernames)
	if not selected:
		return
	info = users[selected]
	with st.form("update_user_form"):
		col1, col2 = st.columns(2)
		with col1:
			new_role = st.selectbox("角色", ["user", "admin"], index=0 if info.get("role")!="admin" else 1)
			new_password = st.text_input("重置密码(留空则不改)", type="password")
		with col2:
			new_perms = st.multiselect("权限", ["analysis", "batch_analysis", "config", "admin"], default=info.get("permissions", []))
		col3, col4 = st.columns(2)
		with col3:
			new_points = st.number_input("点数", min_value=0, value=int(info.get("points", 0)), step=1)
		with col4:
			delta = st.number_input("增减点数(可为负)", value=0, step=1)
		submitted = st.form_submit_button("保存变更")
		if submitted:
			if new_password:
				_ensure_admin_self_protection(selected)
				from web.utils.auth_manager import AuthManager
				hasher = AuthManager()
				info["password_hash"] = hasher._hash_password(new_password)
			info["role"] = new_role
			info["permissions"] = new_perms
			# 点数处理：优先以 new_points 为基准，再叠加 delta
			base_points = int(new_points)
			final_points = int(max(0, base_points + int(delta)))
			info["points"] = final_points
			if _save_users(users):
				st.success("✅ 已保存")
				st.experimental_rerun()


def _delete_user_form(users: dict) -> None:
	st.subheader("🗑️ 删除会员")
	usernames = [u for u in users.keys()]
	if not usernames:
		st.info("暂无用户可删除")
		return
	selected = st.selectbox("选择要删除的用户", usernames)
	if not selected:
		return
	if selected == "admin":
		st.warning("⚠️ 禁止删除内置管理员账户")
		return
	_ensure_admin_self_protection(selected)
	if st.button("确认删除", type="secondary"):
		users.pop(selected, None)
		if _save_users(users):
			st.success("✅ 已删除")
			st.experimental_rerun()


def render_member_management():
	# 权限保护
	if not auth_manager or not auth_manager.check_permission("admin"):
		st.error("❌ 您没有权限访问会员管理")
		return

	st.title("👥 会员管理")
	users = _load_users()

	with st.expander("当前会员", expanded=True):
		_render_users_table(users)

	st.markdown("---")
	col_a, col_b, col_c = st.columns(3)
	with col_a:
		_create_user_form(users)
	with col_b:
		_update_user_form(users)
	with col_c:
		_delete_user_form(users)


def main():
	render_member_management()


