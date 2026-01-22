export default function Footer() {
    return (
        <footer className="bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
                    {/* About */}
                    <div>
                        <div className="flex items-center gap-2 mb-4">
                            <div className="w-6 h-6 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-md flex items-center justify-center">
                                <svg
                                    className="w-4 h-4 text-white"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                                    />
                                </svg>
                            </div>
                            <span className="font-bold text-gray-900 dark:text-white">
                                Codora Timetable
                            </span>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            Deterministic college scheduling with constraint solving.
                        </p>
                    </div>

                    {/* Features */}
                    <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Features</h3>
                        <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                            <li>• Constraint Solving</li>
                            <li>• Data Validation</li>
                            <li>• Calendar View</li>
                            <li>• Human-in-the-Loop</li>
                        </ul>
                    </div>

                    {/* Principles */}
                    <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Core Principles</h3>
                        <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                            <li>✓ Correctness First</li>
                            <li>✓ Transparent</li>
                            <li>✓ Deterministic</li>
                            <li>✓ Explainable</li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-gray-200 dark:border-gray-800 pt-8">
                    <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                            © 2026 Codora. Deterministic scheduling for everyone.
                        </p>
                        <div className="flex items-center gap-6 text-sm text-gray-600 dark:text-gray-400">
                            <a href="https://github.com" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                                GitHub
                            </a>
                            <a href="https://docs.example.com" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                                Docs
                            </a>
                            <a href="https://example.com" className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
                                Website
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    );
}
