import { Alert, Button, Card, Checkbox, Space, Table, Tag, Typography, Upload, message } from "antd";
import type { UploadProps } from "antd";
import { useEffect, useState } from "react";
import { Download, FileSpreadsheet, UploadCloud } from "lucide-react";
import { questionApi } from "../../api/client";
import type { ImportPreview, ImportRecord } from "../../types/domain";
import { shortDate, statusLabel } from "../../utils/format";

function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function QuestionImportPage() {
  const [preview, setPreview] = useState<ImportPreview | null>(null);
  const [records, setRecords] = useState<ImportRecord[]>([]);
  const [autoCreate, setAutoCreate] = useState(true);
  const [skipDuplicates, setSkipDuplicates] = useState(true);
  const [uploading, setUploading] = useState(false);

  const loadRecords = () => questionApi.importRecords({ page_size: 20 }).then((data) => setRecords(data.items));

  useEffect(() => {
    loadRecords();
  }, []);

  const uploadProps: UploadProps = {
    accept: ".xlsx",
    maxCount: 1,
    showUploadList: false,
    customRequest: async ({ file, onSuccess, onError }) => {
      setUploading(true);
      try {
        const data = await questionApi.importPreview(file as File);
        setPreview(data);
        message.success("预览完成");
        onSuccess?.(data);
        loadRecords();
      } catch (error) {
        onError?.(error as Error);
      } finally {
        setUploading(false);
      }
    },
  };

  const confirm = async () => {
    if (!preview) return;
    await questionApi.importConfirm({
      import_record_id: preview.import_record_id,
      auto_create_taxonomy: autoCreate,
      skip_duplicates: skipDuplicates,
    });
    message.success("导入确认完成");
    setPreview(null);
    loadRecords();
  };

  const downloadTemplate = async () => {
    const blob = await questionApi.downloadTemplate();
    saveBlob(blob, "医学刷题题目导入模板.xlsx");
  };

  const exportQuestions = async () => {
    const blob = await questionApi.exportQuestions();
    saveBlob(blob, "医学刷题题库导出.xlsx");
  };

  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <Typography.Title level={2}>批量导入题目</Typography.Title>
          <Typography.Text type="secondary">下载模板、上传 Excel、预览校验，再一键确认入库。</Typography.Text>
        </div>
      </div>
      <div className="panel import-panel">
        <Alert
          type="info"
          showIcon
          message="Excel 模板字段已按后端校验规则设计"
          description="支持自动创建科目、章节和知识点；重复题会在预览阶段标记，确认时可选择跳过。"
        />
        <Space wrap>
          <Button icon={<Download size={16} />} onClick={downloadTemplate}>下载导入模板</Button>
          <Button icon={<FileSpreadsheet size={16} />} onClick={exportQuestions}>导出现有题库</Button>
          <Upload {...uploadProps}>
            <Button type="primary" icon={<UploadCloud size={16} />} loading={uploading}>上传并预览</Button>
          </Upload>
        </Space>
      </div>
      {preview ? (
        <Card variant="borderless" className="section-row">
          <div className="import-summary">
            <Tag color="blue">总计 {preview.total_count}</Tag>
            <Tag color="green">有效 {preview.valid_count}</Tag>
            <Tag color="red">失败 {preview.failed_count}</Tag>
            <Tag color="gold">重复 {preview.duplicate_count}</Tag>
          </div>
          <Space wrap className="section-actions">
            <Checkbox checked={autoCreate} onChange={(event) => setAutoCreate(event.target.checked)}>自动创建分类</Checkbox>
            <Checkbox checked={skipDuplicates} onChange={(event) => setSkipDuplicates(event.target.checked)}>跳过重复题</Checkbox>
            <Button type="primary" onClick={confirm}>确认导入</Button>
          </Space>
          <Table
            rowKey={(row, index) => String(row.row_number || index)}
            dataSource={preview.rows}
            scroll={{ x: 900 }}
            columns={[
              { title: "行号", dataIndex: "row_number", width: 80 },
              { title: "题干", dataIndex: "stem", width: 280 },
              { title: "科目", dataIndex: "subject_name", width: 120 },
              { title: "章节", dataIndex: "chapter_name", width: 140 },
              { title: "知识点", dataIndex: "knowledge_point_name", width: 140 },
              { title: "状态", dataIndex: "status", width: 100, render: (value) => <Tag>{String(value || "-")}</Tag> },
              { title: "错误", dataIndex: "errors", width: 240, render: (value) => Array.isArray(value) ? value.join("；") : String(value || "") },
            ]}
          />
        </Card>
      ) : null}
      <div className="panel section-row">
        <div className="panel-title">导入记录</div>
        <Table
          rowKey="id"
          dataSource={records}
          columns={[
            { title: "文件", dataIndex: "file_name" },
            { title: "状态", dataIndex: "status", render: (value) => <Tag>{statusLabel[String(value)] || String(value)}</Tag> },
            { title: "总数", dataIndex: "total_count" },
            { title: "成功", dataIndex: "success_count" },
            { title: "失败", dataIndex: "failed_count" },
            { title: "重复", dataIndex: "duplicate_count" },
            { title: "时间", dataIndex: "created_at", render: (value) => shortDate(value) },
          ]}
        />
      </div>
    </div>
  );
}