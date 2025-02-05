import { api } from '@/lib/api';

export interface AuthResponse {
    user_id: string;
    telegram_id: string;
}

export const auth = {
    /**
     * Authenticate with Telegram WebApp data
     */
    async authenticateWithTelegram(): Promise<AuthResponse> {
        const webApp = window.Telegram.WebApp;
        
        // Get the raw init data from Telegram WebApp
        const initData = webApp.initData;
        
        if (!initData) {
            throw new Error('No init data available');
        }
        
        // Send raw init data to backend
        const response = await api.post<AuthResponse>('/auth/telegram', {
            init_data: initData
        });
        
        // Store user IDs in localStorage for future use
        localStorage.setItem('user_id', response.data.user_id);
        localStorage.setItem('telegram_id', response.data.telegram_id);
        
        return response.data;
    },
    
    /**
     * Get stored user IDs
     */
    getUserIds(): { userId: string | null; telegramId: string | null } {
        return {
            userId: localStorage.getItem('user_id'),
            telegramId: localStorage.getItem('telegram_id'),
        };
    },
    
    /**
     * Check if user is authenticated
     */
    isAuthenticated(): boolean {
        const { userId, telegramId } = this.getUserIds();
        return Boolean(userId && telegramId);
    },
    
    /**
     * Clear stored authentication data
     */
    logout(): void {
        localStorage.removeItem('user_id');
        localStorage.removeItem('telegram_id');
    },
}; 