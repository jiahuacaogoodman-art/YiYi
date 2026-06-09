import { Col, Empty, Row, Table, Typography } from "antd";
import { useEffect, useMemo, useState } from "react";
import { statisticsApi } from "../../api/client";
import { EChart } from "../../components/EChart";
import type { DashboardStatistics } from "../../types/domain";
import { barOption, lineOption, pieOption } from "../../utils/charts";

export function AdminStatisticsPage() {
  const [stats, setStats] = useState<DashboardStatistics | null>(null);

  useEffect(() => {
    statisticsApi.dashboard().then(setStats);
  }, []);

  const distribution = useMemo(() => {
    const rows = stats?.subject_distribution || [];
    return pieOption(
      "科目题量占比",
      rows.map((row) => ({ name: String(row.subject_name || "-"), value: Number(row.question_count || 0) })),
    );
  }, [stats]);

  const trend = useMemo(() => {
    const rows = stats?.user_practice_trend || [];
    return lineOption(
      "最近 7 天刷题次数",
      rows.map((row) => String(row.date || "")),
      rows.map((row) => Number(row.count || 0)),
    );
  }, [stats]);

  const wrong = useMemo(() => {
    const rows = stats?.top_wrong_knowledge_points || [];
    return barOption(
      "高错误率知识点",
      rows.map((row) => String(row.knowledge_point_name || "")),
      rows.map((row) => Number(row.wrong_rate || 0)),
    );
  }, [stats]);

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>数据统计</Typography.Title>
          <Typography.Text type="secondary">从题库分布、用户活跃和知识点错误率观察运营质量。</Typography.Text>
        </div>
      </div>
      <Row gutter={[16, 16]}>
        <Col xs={24} xl={8}>
          <div className="panel">{stats?.subject_distribution?.length ? <EChart option={distribution} height={330} /> : <Empty description="暂无题量分布" />}</div>
        </Col>
        <Col xs={24} xl={8}>
          <div className="panel">{stats?.user_practice_trend?.length ? <EChart option={trend} height={330} /> : <Empty description="暂无活跃趋势" />}</div>
        </Col>
        <Col xs={24} xl={8}>
          <div className="panel">{stats?.top_wrong_knowledge_points?.length ? <EChart option={wrong} height={330} /> : <Empty description="暂无错误率数据" />}</div>
        </Col>
      </Row>
      <div className="panel section-row">
        <div className="panel-title">错误率最高的知识点</div>
        <Table
          rowKey={(row) => String(row.knowledge_point_id)}
          dataSource={stats?.top_wrong_knowledge_points || []}
          pagination={false}
          columns={[
            { title: "知识点", dataIndex: "knowledge_point_name" },
            { title: "错误次数", dataIndex: "wrong_count" },
            { title: "错误率", dataIndex: "wrong_rate", render: (value) => `${Number(value || 0).toFixed(1)}%` },
          ]}
        />
      </div>
    </div>
  );
}