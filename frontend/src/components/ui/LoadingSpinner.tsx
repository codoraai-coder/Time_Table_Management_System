interface LoadingSpinnerProps {
    size?: 'sm' | 'md' | 'lg';
    text?: string;
    className?: string;
}

export default function LoadingSpinner({
    size = 'md',
    text,
    className = '',
}: LoadingSpinnerProps) {
    const sizes = {
        sm: 'h-8 w-8 border-3',
        md: 'h-14 w-14 border-4',
        lg: 'h-20 w-20 border-5',
    };

    return (
        <div className={`flex flex-col items-center justify-center gap-6 ${className}`}>
            <div className="relative">
                {/* Outer spinning border */}
                <div
                    className={`${sizes[size]} animate-spin rounded-full border-transparent bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600`}
                    style={{
                        borderTopColor: '#4f46e5',
                        borderRightColor: '#9333ea',
                        borderBottomColor: '#ec4899',
                        borderLeftColor: 'transparent',
                    }}
                ></div>
                {/* Inner decorative element */}
                <div
                    className={`${sizes[size]} absolute top-0 left-0 animate-pulse rounded-full bg-gradient-to-br from-indigo-200 to-purple-200 dark:from-indigo-800 dark:to-purple-800 opacity-20`}
                ></div>
            </div>
            {text && (
                <div className="text-center space-y-2">
                    <p className="text-base font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                        {text}
                    </p>
                    <div className="flex justify-center gap-1">
                        {[0, 1, 2].map((i) => (
                            <div
                                key={i}
                                className="w-1.5 h-1.5 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full animate-bounce"
                                style={{animationDelay: `${i * 150}ms`}}
                            ></div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
