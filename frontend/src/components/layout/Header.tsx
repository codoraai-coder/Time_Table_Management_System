'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navigation = [
    { name: 'Upload', href: '/upload' },
    { name: 'Timetable', href: '/timetable' },
];

export default function Header() {
    const pathname = usePathname();

    return (
        <header className="sticky top-0 z-50 backdrop-blur-2xl bg-white/80 dark:bg-gray-900/80 border-b border-gradient-to-r from-indigo-200 via-purple-200 to-pink-200 dark:border-gray-800/50 shadow-xl">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-20">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-3 group hover:opacity-90 transition-opacity">
                        <div className="w-12 h-12 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 rounded-2xl flex items-center justify-center shadow-2xl group-hover:shadow-pink-500/50 group-hover:shadow-2xl transition-all duration-300 transform group-hover:scale-110">
                            <span className="text-xl group-hover:animate-spin" style={{animationDuration: '2s'}}>⏱️</span>
                        </div>
                        <div className="hidden sm:block">
                            <span className="font-black text-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent block leading-tight">
                                TimeTable
                            </span>
                            <span className="text-xs text-gray-500 dark:text-gray-400 font-semibold">Management System</span>
                        </div>
                    </Link>

                    {/* Navigation */}
                    <nav className="hidden md:flex items-center gap-1">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={`px-4 py-2.5 rounded-xl font-bold transition-all duration-300 relative group ${
                                        isActive
                                            ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-xl'
                                            : 'text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400'
                                    }`}
                                >
                                    {item.name}
                                    {!isActive && (
                                        <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-indigo-600 to-purple-600 group-hover:w-full transition-all duration-300"></span>
                                    )}
                                </Link>
                            );
                        })}
                    </nav>

                    {/* Status Badge */}
                    <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 border border-green-300 dark:border-green-800">
                        <div className="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></div>
                        <span className="text-sm font-bold text-green-700 dark:text-green-300">Live</span>
                    </div>
                </div>
            </div>
        </header>
    );
}
