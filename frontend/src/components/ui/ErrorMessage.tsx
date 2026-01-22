interface ErrorMessageProps {
    message: string;
    title?: string;
    onRetry?: () => void;
    className?: string;
}

export default function ErrorMessage({
    message,
    title = 'An error occurred',
    onRetry,
    className = '',
}: ErrorMessageProps) {
    return (
        <div
            className={`rounded-3xl bg-gradient-to-br from-red-50 via-rose-50 to-red-50 dark:from-red-900/30 dark:via-rose-900/30 dark:to-red-900/30 border-2 border-red-300 dark:border-red-700 p-8 shadow-xl hover:shadow-2xl transition-all duration-300 ${className}`}
        >
            <div className="flex items-start gap-5">
                <div className="flex-shrink-0 mt-1">
                    <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-rose-500 rounded-2xl flex items-center justify-center shadow-lg">
                        <svg
                            className="h-6 w-6 text-white"
                            fill="none"
                            viewBox="0 0 24 24"
                            strokeWidth="2.5"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
                            />
                        </svg>
                    </div>
                </div>
                <div className="flex-1">
                    <h3 className="text-xl font-bold text-red-900 dark:text-red-100">{title}</h3>
                    <p className="mt-3 text-base text-red-800 dark:text-red-200 leading-relaxed">{message}</p>
                    {onRetry && (
                        <button
                            onClick={onRetry}
                            className="mt-6 px-6 py-2.5 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 text-white font-bold rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl active:scale-95"
                        >
                            Try again
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
