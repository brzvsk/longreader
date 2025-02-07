"use client"

import { useAuth } from '@/components/providers/auth-provider';

interface RequireAuthProps {
    children: React.ReactNode;
}

export function RequireAuth({ children }: RequireAuthProps) {
    const { isAuthenticated, isLoading, error } = useAuth();

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
                    <p className="mt-4">Loading...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center p-4">
                    <h1 className="text-xl font-semibold mb-2">Authentication Required</h1>
                    {error && (
                        <p className="text-red-600">
                            Error: {error}
                        </p>
                    )}
                </div>
            </div>
        );
    }

    return <>{children}</>;
} 