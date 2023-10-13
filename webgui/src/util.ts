export const shuffle = <T>(array: T[]) => {
	for (let i = array.length - 1; i > 0; i--) {
		const j = Math.floor(Math.random() * (i + 1));
		[array[i], array[j]] = [array[j], array[i]];
	}
	return array;
};

export const debounce = <T extends (...args: Parameters<T>) => void>(
	callback: T,
	wait: number,
	immediate = false,
) => {
	let timeoutID = -1;

	return function <U>(this: U, ...args: Parameters<typeof callback>) {
		const context = this;
		const later = () => {
			timeoutID = -1;

			if (!immediate) {
				callback.apply(context, args);
			}
		};

		if (timeoutID > -1) clearTimeout(timeoutID);
		timeoutID = setTimeout(later, wait);

		const callNow = immediate && !timeoutID;
		if (callNow) {
			callback.apply(context, args);
		}
	};
};
