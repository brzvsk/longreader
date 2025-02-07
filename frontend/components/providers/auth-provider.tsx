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
            console.log('Starting authentication process...');
            try {
                setError(null);
                // Check if we have stored auth data
                console.log('Checking stored auth data...');
                if (auth.isAuthenticated()) {
                    console.log('Found stored auth data');
                    const { userId, telegramId } = auth.getUserIds();
                    console.log('User IDs retrieved:', { userId, telegramId });
                    
                    setAuthState({
                        isAuthenticated: true,
                        userId,
                        telegramId,
                    });
                } else {
                    console.log('No stored auth data found');
                    // Only check Telegram WebApp on client side
                    console.log('Checking Telegram WebApp availability:', {
                        window: !!window,
                        TelegramObj: !!window?.Telegram,
                        WebAppObj: !!window?.Telegram?.WebApp
                    });
                    
                    if (!window?.Telegram?.WebApp) {
                        throw new Error('This app must be opened in Telegram');
                    }
                    // Try to authenticate with Telegram
                    console.log('Attempting Telegram authentication...');
                    const response = await auth.authenticateWithTelegram();
                    console.log('Telegram authentication response:', response);
                    
                    setAuthState({
                        isAuthenticated: true,
                        userId: response.user_id,
                        telegramId: response.telegram_id,
                    });
                }
            } catch (error) {
                console.error('Authentication error:', error);
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