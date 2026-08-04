// ===== User =====
export interface User {
  id: number
  username: string
  email: string
  avatar_url?: string
  role: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// ===== API Provider =====
export type ProviderType = 'image' | 'video' | 'chat'

export interface APIProvider {
  id: number
  name: string
  provider_type: ProviderType
  base_url: string
  api_key: string
  is_default: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ProviderFormData {
  name: string
  provider_type: ProviderType
  base_url: string
  api_key: string
  is_default?: boolean
}

// ===== Generation =====
export type GenerationStatus = 'pending' | 'processing' | 'completed' | 'failed'
export type GenerationType = 'image' | 'video'

export interface Generation {
  id: number
  type: GenerationType
  prompt: string
  status: GenerationStatus
  progress: number
  result_url?: string
  thumbnail_url?: string
  params: Record<string, any>
  error_message?: string
  created_at: string
  updated_at: string
}

// ===== Chat =====
export type ChatRole = 'user' | 'assistant' | 'system' | 'tool'

export interface ChatMessage {
  id: string
  role: ChatRole
  content: string
  tool_calls?: ToolCall[]
  tool_call_id?: string
  created_at: string
}

export interface ToolCall {
  id: string
  name: string
  arguments: string
  result?: string
}

export interface ChatHistory {
  id: number
  title: string
  messages: ChatMessage[]
  created_at: string
  updated_at: string
}

// ===== Image Generation =====
export interface ImageGenerationParams {
  prompt: string
  negative_prompt?: string
  model?: string
  width?: number
  height?: number
  aspect_ratio?: string
  num_images?: number
  seed?: number
  image_url?: string
  strength?: number
}

// ===== Video Generation =====
export interface VideoGenerationParams {
  prompt: string
  negative_prompt?: string
  model?: string
  width?: number
  height?: number
  duration?: number
  fps?: number
  num_frames?: number
  seed?: number
  image_url?: string
  keyframe_urls?: string[]
}

// ===== API Response =====
export interface ApiResponse<T> {
  data: T
  message: string
  success: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// ===== Auth =====
export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

// ===== Config =====
export interface AppConfig {
  max_image_size: number
  supported_image_formats: string[]
  supported_video_formats: string[]
  max_prompt_length: number
  features: Record<string, boolean>
}

// ===== History =====
export interface HistoryFilter {
  type?: GenerationType
  start_date?: string
  end_date?: string
  search?: string
  page?: number
  page_size?: number
}

// ===== SSE Event =====
export interface SSEChatEvent {
  type: 'content' | 'tool_call' | 'tool_result' | 'done' | 'error'
  content?: string
  tool_call?: ToolCall
  error?: string
}