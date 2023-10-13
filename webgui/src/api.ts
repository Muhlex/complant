export const HOST_IP = "192.168.6.1";
const BASE_URL = `http://${HOST_IP}/api/`;

export class HTTPError extends Error {
	status: number;

	constructor(status: number, reason?: string) {
		super(reason);
		this.name = "HTTPError";
		this.status = status;
		this.message = `(${this.status}) ${this.message}`;
	}
}

type RequestOptions = {
	host?: string
	method?: string
	json?: object
}
export async function request(endpoint: string, options?: RequestOptions) {
	try {
		options ??= {};
		options = Object.assign({ method: "GET" }, options);
		const url = new URL(endpoint, BASE_URL);
		if (options.host) url.host = options.host;
		const headers: HeadersInit = {};
		if (options.json) headers["Content-Type"] = "application/json";
		const response = await fetch(url, {
			method: options.method,
			body: options.json ? JSON.stringify(options.json) : null,
			headers,
		});
		const resJson = response.status === 204 ? {} : await response.json();
		if (!response.ok) {
			throw new HTTPError(response.status, resJson.error);
		}
		return resJson;
	} catch (error) {
		console.error(error);
	}
}
