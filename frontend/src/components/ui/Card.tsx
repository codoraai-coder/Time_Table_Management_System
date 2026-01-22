import { ReactNode } from 'react';

interface CardProps {
    children: ReactNode;
    className?: string;
    title?: string;
    subtitle?: string;
    variant?: 'default' | 'glass' | 'bordered';
}

export default function Card({
    children,
    className = '',
    title,
    subtitle,
    variant = 'default',
}: CardProps) {
    const variants = {
        default: 'bg-white dark:bg-gray-900 shadow-xl border border-gray-200 dark:border-gray-800 hover:shadow-2xl transition-shadow duration-300',
        glass: 'bg-gradient-to-br from-white/90 to-gray-50/90 dark:from-gray-900/90 dark:to-gray-800/90 backdrop-blur-2xl shadow-2xl border border-white/30 dark:border-gray-700/30 hover:shadow-3xl transition-all duration-300',
        bordered: 'bg-gradient-to-br from-white to-gray-50 dark:from-gray-900 dark:to-gray-800 border-2 border-gradient-to-r border-indigo-300 dark:border-indigo-700 shadow-xl hover:shadow-2xl transition-all duration-300',
    };

    return (
        <div
            className={`rounded-2xl p-6 ${variants[variant]} ${className}`}
        >
            {(title || subtitle) && (
                <div className="mb-6 pb-6 border-b border-gray-200 dark:border-gray-700">
                    {title && (
                        <h3 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">{title}</h3>
                    )}
                    {subtitle && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">{subtitle}</p>
                    )}
                </div>
            )}
            {children}
        </div>
    );
}
