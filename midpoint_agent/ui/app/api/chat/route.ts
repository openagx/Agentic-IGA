import { NextRequest, NextResponse } from 'next/server'
import Anthropic from '@anthropic-ai/sdk'

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY || process.env.LLM_API_KEY,
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { message } = body

    if (!message) {
      return NextResponse.json({ error: 'Message is required' }, { status: 400 })
    }

    const systemPrompt = `You are a helpful assistant for midPoint identity management.
midPoint is an open-source identity governance and administration (IGA) system.
You help users manage users, roles, organizations, resources, and access policies.
Provide clear, accurate information about identity management concepts.`

    const response = await anthropic.messages.create({
      model: process.env.LLM_MODEL || 'claude-sonnet-4-20250514',
      max_tokens: 1024,
      system: systemPrompt,
      messages: [
        { role: 'user', content: message }
      ]
    })

    const responseText = response.content[0].type === 'text' 
      ? response.content[0].text 
      : 'No response'

    return NextResponse.json({ response: responseText })
  } catch (error) {
    console.error('Chat error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal error' },
      { status: 500 }
    )
  }
}