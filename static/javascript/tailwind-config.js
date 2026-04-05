/**
 * Tailwind CSS Configuration
 * Configures custom theme colors, fonts, and utilities
 * Auto-restarts after configuration to apply custom styles
 */

tailwind.config = {
    theme: {
        extend: {
            colors: {
                background: '#FDFCF8',
                foreground: '#2C2C24',
                primary: { DEFAULT: '#5D7052', foreground: '#F3F4F1' },
                secondary: { DEFAULT: '#C18C5D', foreground: '#FFFFFF' },
                accent: { DEFAULT: '#E6DCCD', foreground: '#4A4A40' },
                muted: { DEFAULT: '#F0EBE5', foreground: '#78786C' },
                border: '#DED8CF',
                destructive: '#A85448',
            },
            fontFamily: {
                sans: ['Nunito', 'sans-serif'],
                serif: ['Fraunces', 'serif'],
            },
            boxShadow: {
                soft: '0 4px 20px -2px rgba(93, 112, 82, 0.15)',
                float: '0 10px 40px -10px rgba(193, 140, 93, 0.2)',
            },
            borderRadius: {
                'organic-1': '60% 40% 30% 70% / 60% 30% 70% 40%',
                'organic-2': '30% 70% 70% 30% / 30% 30% 70% 70%',
                'organic-3': '50% 50% 20% 80% / 25% 80% 20% 75%',
            }
        }
    }
};

// Force Tailwind to rebuild with custom config
if (window.tailwind) {
    window.tailwind.restart();
}
