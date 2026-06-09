import type { EChartsOption } from "echarts";

export function lineOption(title: string, labels: string[], values: number[]): EChartsOption {
  return {
    color: ["#4c7dff", "#16b873"],
    title: { text: title, textStyle: { fontSize: 14, fontWeight: 700, color: "#1d2636" }, left: 0 },
    tooltip: { trigger: "axis" },
    grid: { left: 32, right: 16, top: 44, bottom: 28 },
    xAxis: { type: "category", data: labels, axisTick: { show: false }, axisLine: { lineStyle: { color: "#ded5c5" } } },
    yAxis: { type: "value", splitLine: { lineStyle: { color: "#eee8dd" } } },
    series: [{ type: "line", smooth: true, data: values, areaStyle: { opacity: 0.14 }, lineStyle: { width: 3 } }],
  };
}

export function barOption(title: string, labels: string[], values: number[]): EChartsOption {
  return {
    color: ["#4c7dff"],
    title: { text: title, textStyle: { fontSize: 14, fontWeight: 700, color: "#1d2636" }, left: 0 },
    tooltip: { trigger: "axis" },
    grid: { left: 36, right: 16, top: 44, bottom: 36 },
    xAxis: { type: "category", data: labels, axisLabel: { interval: 0, rotate: labels.length > 6 ? 24 : 0 }, axisLine: { lineStyle: { color: "#ded5c5" } } },
    yAxis: { type: "value", splitLine: { lineStyle: { color: "#eee8dd" } } },
    series: [{ type: "bar", data: values, barMaxWidth: 34, itemStyle: { borderRadius: [6, 6, 0, 0] } }],
  };
}

export function pieOption(title: string, data: Array<{ name: string; value: number }>): EChartsOption {
  return {
    color: ["#4c7dff", "#16b873", "#ff9f2d", "#78a2ff", "#9bb8ff", "#dce8ff"],
    title: { text: title, textStyle: { fontSize: 14, fontWeight: 700, color: "#1d2636" }, left: 0 },
    tooltip: { trigger: "item" },
    legend: { bottom: 0, type: "scroll" },
    series: [{ type: "pie", radius: ["42%", "68%"], center: ["50%", "45%"], data }],
  };
}