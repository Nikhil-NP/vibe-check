import { useState, useEffect } from 'react';

export default function ColdStartNotice() {
    const [visible, setVisible] = useState(true);

    // Auto-dismiss after 15 seconds if they don't manually close it
    useEffect(() => {
        const timer = setTimeout(() => setVisible(false), 15000);
        return () => clearTimeout(timer);
    }, []);

    if (!visible) return null;

    return (
        <div className="fixed bottom-4 right-4 z-50 animate-fade-in-up max-w-sm w-full mx-4 sm:mx-0">
            <div className="bg-white/90 backdrop-blur-md border border-amber-200 shadow-2xl rounded-2xl p-4 relative overflow-hidden">
                {/* Progress bar for auto-dismiss */}
                <div className="absolute bottom-0 left-0 h-1 bg-amber-200 w-full">
                    <div
                        className="h-full bg-amber-500 transition-all duration-[15000ms] ease-linear w-0 animate-progress-grow"
                        style={{ width: '100%' }}
                    />
                </div>

                <div className="flex items-start gap-3">
                    <div className="bg-amber-100 p-2 rounded-full shrink-0">
                        <span className="text-xl">⏳</span>
                    </div>
                    <div className="flex-1">
                        <div className="flex justify-between items-start">
                            <h4 className="font-bold text-gray-800 text-sm mb-1">Cold Start Warning</h4>
                            <button
                                onClick={() => setVisible(false)}
                                className="text-gray-400 hover:text-gray-600 transition -mt-1 -mr-1 p-1"
                            >
                                ✕
                            </button>
                        </div>
                        <p className="text-xs text-gray-600 leading-relaxed">
                            Using a free tier backend. The first request might take <span className="font-bold text-amber-600">up to 30-50 seconds</span> to spin up. Please be patient or refresh if it times out!
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
