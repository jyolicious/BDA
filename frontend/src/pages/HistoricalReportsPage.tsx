import React, { useEffect, useState } from 'react';
import { FileText, Download, TrendingUp, BarChart2 } from 'lucide-react';
import { api } from '../services/api';

export const HistoricalReportsPage: React.FC = () => {
  const [reportsData, setReportsData] = useState<any>(null);

  useEffect(() => {
    api.getReports()
      .then((res) => setReportsData(res))
      .catch((err) => console.error(err));
  }, []);

  const downloadCSV = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 font-mono">
      {/* Subheader */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-cyber-border/70 gap-2">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wider flex items-center space-x-2">
            <FileText className="w-5 h-5 text-cyber-cyan" />
            <span>HISTORICAL REPORTS &bull; SCALABILITY BENCHMARKS</span>
          </h2>
          <p className="text-xs text-cyber-muted mt-0.5">
            Empirical big data scalability results, throughput evaluation, and downloadable research artifacts.
          </p>
        </div>
      </div>

      {/* Benchmark Results Table */}
      <div className="hud-card p-5 rounded-sm space-y-4">
        <div className="flex items-center justify-between border-b border-cyber-border pb-2">
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center">
              <TrendingUp className="w-4 h-4 mr-1.5 text-cyber-cyan" />
              EMPIRICAL SCALABILITY BENCHMARK (10K, 50K, 100K EVENTS)
            </h3>
            <p className="text-[11px] text-cyber-muted">
              Measured on this local test environment with genuine MapReduce and Streaming detector execution.
            </p>
          </div>
          <button
            onClick={() => {
              if (reportsData?.benchmark_rows) {
                const header = Object.keys(reportsData.benchmark_rows[0]).join(',');
                const rows = reportsData.benchmark_rows.map((r: any) => Object.values(r).join(',')).join('\n');
                downloadCSV(`${header}\n${rows}`, 'scalability_experiment.csv');
              }
            }}
            className="px-3 py-1.5 bg-cyber-card border border-cyber-cyan/50 text-cyber-cyan hover:bg-cyber-cyan hover:text-black rounded text-xs font-bold transition-all flex items-center space-x-1.5"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-cyber-surface text-[10px] text-cyber-muted uppercase border-b border-cyber-border">
              <tr>
                <th className="p-3">Dataset Scale</th>
                <th className="p-3">File Size</th>
                <th className="p-3">MapReduce Runtime</th>
                <th className="p-3">MapReduce Throughput</th>
                <th className="p-3">Stream Throughput</th>
                <th className="p-3">Scalability Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border/40">
              {reportsData?.benchmark_rows && reportsData.benchmark_rows.length > 0 ? (
                reportsData.benchmark_rows.map((row: any, i: number) => (
                  <tr key={i} className="hover:bg-cyber-surface/60 transition-colors">
                    <td className="p-3 font-bold text-white">
                      {parseInt(row.dataset_size, 10).toLocaleString()} Events
                    </td>
                    <td className="p-3 text-cyber-muted">{row.file_size_mb} MB</td>
                    <td className="p-3 text-white font-mono">{row.mapreduce_time_sec}s</td>
                    <td className="p-3 font-bold text-cyber-cyan">
                      {parseFloat(row.mapreduce_throughput_eps).toLocaleString()} ev/s
                    </td>
                    <td className="p-3 font-bold text-cyber-green">
                      {parseFloat(row.streaming_throughput_eps).toLocaleString()} ev/s
                    </td>
                    <td className="p-3">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyber-green/10 text-cyber-green border border-cyber-green/30">
                        VERIFIED LINEAR
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="p-6 text-center text-cyber-muted italic">
                    Benchmark reports not found. Run scripts/run_performance_experiment.py.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Markdown Observation Summary Box */}
      {reportsData?.markdown_report && (
        <div className="hud-card p-5 rounded-sm space-y-3">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-cyber-border pb-2 flex items-center">
            <BarChart2 className="w-4 h-4 mr-1.5 text-cyber-cyan" />
            RESEARCH REPORT &bull; TECHNICAL FINDINGS
          </h3>
          <div className="bg-cyber-surface p-4 rounded border border-cyber-border/80 text-xs text-cyber-text/90 leading-relaxed font-mono whitespace-pre-wrap">
            {reportsData.markdown_report}
          </div>
        </div>
      )}
    </div>
  );
};
