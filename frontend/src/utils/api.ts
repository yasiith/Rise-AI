

export const fetchApi = async <T>(url: string, options: RequestInit = {}): Promise<{ success: boolean; data?: T; error?: string }> => {
  try {
    // Get API URL from environment or fallback to localhost
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
    console.log(`API call to: ${baseUrl}${url}`);
    
    const response = await fetch(`${baseUrl}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    console.error('API Error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
};