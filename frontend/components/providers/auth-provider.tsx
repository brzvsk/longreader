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
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [authState, setAuthState] = useState<Omit<AuthContextType, 'isLoading' | 'error'>>({
        isAuthenticated: false,
        userId: null,
        telegramId: null,
    });

    useEffect(() => {
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
                    // Check if we're in Telegram Web App environment
                    if (!window.Telegram?.WebApp) {
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
                console.error('Authentication failed:', error);
                setError(error instanceof Error ? error.message : 'Authentication failed');
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
    }, []);

    return (
        <AuthContext.Provider value={{ ...authState, isLoading, error }}>
            {children}
        </AuthContext.Provider>
    );
} 