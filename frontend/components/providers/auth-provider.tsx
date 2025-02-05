"use client"

import { createContext, useContext, useEffect, useState } from 'react';
import { auth } from '@/services/auth';

interface AuthContextType {
    isAuthenticated: boolean;
    userId: string | null;
    telegramId: string | null;
    isLoading: boolean;
    error: string | null;
}

const AuthContext = createContext<AuthContextType>({
    isAuthenticated: false,
    userId: null,
    telegramId: null,
    isLoading: true,
    error: null,
});

export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [mounted, setMounted] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [authState, setAuthState] = useState<Omit<AuthContextType, 'isLoading' | 'error'>>({
        isAuthenticated: false,
        userId: null,
        telegramId: null,
    });

    // First effect just to mark component as mounted
    useEffect(() => {
        setMounted(true);
    }, []);

    // Main auth effect that only runs after component is mounted
    useEffect(() => {
        if (!mounted) return;
        
        const initAuth = async () => {
            try {
                setError(null);
                // Check if we have stored auth data
                if (auth.isAuthenticated()) {
                    const { userId, telegramId } = auth.getUserIds();
                    
                    setAuthState({
                        isAuthenticated: true,
                        userId,
                        telegramId,
                    });
                } else {
                    // Only check Telegram WebApp on client side
                    if (!window?.Telegram?.WebApp) {
                        throw new Error('This app must be opened in Telegram');
                    }
                    // Try to authenticate with Telegram
                    const response = await auth.authenticateWithTelegram();
                    
                    setAuthState({
                        isAuthenticated: true,
                        userId: response.user_id,
                        telegramId: response.telegram_id,
                    });
                }
            } catch (error) {
                const errorMessage = error instanceof Error ? error.message : 'Authentication failed';
                setError(errorMessage);
                setAuthState({
                    isAuthenticated: false,
                    userId: null,
                    telegramId: null,
                });
            } finally {
                setIsLoading(false);
            }
        };

        initAuth();
    }, [mounted]);

    // During SSR and first render, return a loading state
    if (!mounted) {
        return (
            <AuthContext.Provider value={{
                isAuthenticated: false,
                userId: null,
                telegramId: null,
                isLoading: true,
                error: null
            }}>
                {children}
            </AuthContext.Provider>
        );
    }

    return (
        <AuthContext.Provider value={{ ...authState, isLoading, error }}>
            {children}
        </AuthContext.Provider>
    );
} 