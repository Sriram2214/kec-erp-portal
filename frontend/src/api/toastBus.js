export const toastEvents = {
  queue: [],
  listener: null,
  
  emit(message, type) {
    if (this.listener) {
      this.listener(message, type)
    } else {
      this.queue.push({ message, type })
    }
  },
  
  subscribe(callback) {
    this.listener = callback
    while (this.queue.length > 0) {
      const { message, type } = this.queue.shift()
      callback(message, type)
    }
    return () => { this.listener = null }
  }
}
