'use client';

import { useState, useEffect } from 'react';

interface CsvPreviewProps {
    file: File;
}

export default function CsvPreview({ file }: CsvPreviewProps) {
    const [data, setData] = useState<string[][]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const text = e.target?.result as string;
            // Simple CSV parser
            const rows = text.split('\n').map(row => row.split(',').map(cell => cell.trim()));
            setData(rows.slice(0, 10)); // Top 10 rows
            setLoading(false);
        };
        reader.readAsText(file);
    }, [file]);

    if (loading) return <div className="p-8 text-center text-gray-500">Loading preview...</div>;

    return (
        <div className="w-full overflow-hidden rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm bg-white dark:bg-gray-900">
            <div className="bg-emerald-50 dark:bg-emerald-900/20 p-4 border-b border-emerald-100 dark:border-emerald-800/30 flex justify-between items-center">
                <div>
                    <h3 className="font-bold text-emerald-900 dark:text-emerald-200 flex items-center gap-2">
                        <span>📄</span> {file.name}
                    </h3>
                    <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-1">Showing first 10 rows</p>
                </div>
                <span className="text-xs font-mono bg-emerald-100 dark:bg-emerald-800/50 px-2 py-1 rounded text-emerald-700 dark:text-emerald-300">CSV Preview</span>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-800 dark:text-gray-400">
                        <tr>
                            {data[0]?.map((header, i) => (
                                <th key={i} className="px-6 py-3">{header}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data.slice(1).map((row, i) => (
                            <tr key={i} className="bg-white border-b dark:bg-gray-900 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700/[.05]">
                                {row.map((cell, j) => (
                                    <td key={j} className="px-6 py-4 truncate max-w-[200px]">{cell}</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
