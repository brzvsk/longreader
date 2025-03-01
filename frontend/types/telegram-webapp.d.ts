interface TelegramUser {
    id: number;
    first_name?: string;
    last_name?: string;
    username?: string;
    language_code?: string;
    allows_write_to_pm?: boolean;
}

interface WebAppInitData {
    query_id?: string;
    user?: string;
    receiver?: string;
    start_param?: string;
    auth_date: number;
    hash: string;
}

interface WebAppUser extends TelegramUser {
    is_premium?: boolean;
}

interface WebApp {
    initData: string;
    initDataUnsafe: WebAppInitData & {
        user?: WebAppUser;
    };
    platform: string;
    colorScheme: string;
    themeParams: {
        bg_color: string;
        text_color: string;
        hint_color: string;
        link_color: string;
        button_color: string;
        button_text_color: string;
    };
    isExpanded: boolean;
    viewportHeight: number;
    viewportStableHeight: number;
    BackButton: {
        show: () => void;
        hide: () => void;
        onClick: (callback: () => void) => void;
    };
    ready(): void;
    expand(): void;
    close(): void;
    showConfirm(message: string, callback?: (isConfirmed: boolean) => void): void;
    showAlert(message: string): Promise<void>;
    hapticFeedback: {
        impactOccurred(style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft'): void;
        notificationOccurred(type: 'error' | 'warning' | 'success'): void;
    };
    shareMessage(messageId: string, callback: (success: boolean) => void): void;
}

interface Window {
    Telegram: {
        WebApp: WebApp;
    };
} 