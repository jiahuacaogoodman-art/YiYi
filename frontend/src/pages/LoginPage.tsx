import { Button, Card, Form, Input, Segmented, Typography, message } from "antd";
import { useState } from "react";
import { Activity, Lock, UserRound } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { authApi } from "../api/client";
import { useAuthStore } from "../stores/authStore";

export function LoginPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [loading, setLoading] = useState(false);
  const login = useAuthStore((state) => state.login);
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: string } | null)?.from || "/";

  const submit = async (values: { username: string; password: string; nickname?: string; email?: string }) => {
    setLoading(true);
    try {
      if (mode === "register") {
        await authApi.register(values);
        message.success("注册成功，正在登录");
      }
      const user = await login(values.username, values.password);
      navigate(user.role.name === "student" ? from : "/admin", { replace: true });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-visual">
        <div className="login-visual__content">
          <Activity size={44} />
          <Typography.Title>医学刷题平台</Typography.Title>
          <Typography.Paragraph>
            面向医学生、执业医师考试和期末复习的中文题库系统，学生刷题和后台维护在同一套工作台里完成。
          </Typography.Paragraph>
        </div>
      </section>
      <Card className="login-card" variant="borderless">
        <Segmented
          block
          value={mode}
          onChange={(value) => setMode(value as "login" | "register")}
          options={[
            { label: "登录", value: "login" },
            { label: "注册学生账号", value: "register" },
          ]}
        />
        <Form layout="vertical" className="login-form" onFinish={submit} initialValues={{ username: "admin", password: "admin123456" }}>
          <Form.Item label="用户名" name="username" rules={[{ required: true, message: "请输入用户名" }]}>
            <Input prefix={<UserRound size={16} />} placeholder="admin" />
          </Form.Item>
          {mode === "register" ? (
            <>
              <Form.Item label="昵称" name="nickname">
                <Input placeholder="例如：临床一班张同学" />
              </Form.Item>
              <Form.Item label="邮箱" name="email">
                <Input placeholder="可选" />
              </Form.Item>
            </>
          ) : null}
          <Form.Item label="密码" name="password" rules={[{ required: true, message: "请输入密码" }]}>
            <Input.Password prefix={<Lock size={16} />} placeholder="admin123456" />
          </Form.Item>
          <Button type="primary" htmlType="submit" size="large" block loading={loading}>
            {mode === "login" ? "进入系统" : "注册并进入"}
          </Button>
        </Form>
      </Card>
    </main>
  );
}