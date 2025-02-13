import axios from 'axios';

// Create axios instance with default config
export const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://api.longreader.brzv.sk/',
    headers: {
        'Content-Type': 'application/json',
    },
}); 
