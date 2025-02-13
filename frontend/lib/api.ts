import axios from 'axios';

// Create axios instance with default config
export const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://longreader.brzv.sk/api',
    headers: {
        'Content-Type': 'application/json',
    },
}); 
