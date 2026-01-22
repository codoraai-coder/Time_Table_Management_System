interface StatusBadgeProps {
    status: 'success' | 'warning' | 'error' | 'info' | 'pending';
    text: string;
    className?: string;
}

export default function StatusBadge({
    status,
    text,
    className = '',
}: StatusBadgeProps) {
    const statusStyles = {
        success: 'bg-emerald-100 text-emerald-800 border-emerald-200',
        warning: 'bg-amber-100 text-amber-800 border-amber-200',
        error: 'bg-red-100 text-red-800 border-red-200',
        info: 'bg-blue-100 text-blue-800 border-blue-200',
        pending: 'bg-gray-100 text-gray-800 border-gray-200',
    };

    const dotStyles = {
        success: 'bg-emerald-500',
        warning: 'bg-amber-500',
        error: 'bg-red-500',
        info: 'bg-blue-500',
        pending: 'bg-gray-500 animate-pulse',
    };

    return (
        <span
            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${statusStyles[status]} ${className}`}
        >
            <span className={`w-1.5 h-1.5 rounded-full ${dotStyles[status]}`}></span>
            {text}
        </span>
    );
}
