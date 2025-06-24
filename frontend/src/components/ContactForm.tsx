// src/components/ContactForm.tsx

import { useState } from 'react'

const ContactForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  })
  const [submitted, setSubmitted] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const res = await fetch('http://localhost:8000/api/contact/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })

    if (res.ok) {
      setSubmitted(true)
      setFormData({ name: '', email: '', message: '' })
    }
  }

  return (
    <section className="p-6">
      <h2 className="text-3xl font-bold mb-4">Contact Me</h2>
      {submitted ? (
        <p className="text-green-600">Thanks! Your message has been sent.</p>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
          <input
            type="text"
            name="name"
            value={formData.name}
            placeholder="Your Name"
            onChange={handleChange}
            className="w-full p-2 border rounded"
            required
          />
          <input
            type="email"
            name="email"
            value={formData.email}
            placeholder="Your Email"
            onChange={handleChange}
            className="w-full p-2 border rounded"
            required
          />
          <textarea
            name="message"
            value={formData.message}
            placeholder="Your Message"
            onChange={handleChange}
            className="w-full p-2 border rounded"
            rows={4}
            required
          />
          <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Send
          </button>
        </form>
      )}
    </section>
  )
}

export default ContactForm
