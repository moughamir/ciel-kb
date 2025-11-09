// scripts/chat_types.ts

export type AllChatArray = ChatFolder[];

export interface ChatFolder {
  id: string;
  user_id: string;
  title: string;
  chat: ChatType;
  updated_at: number;
  created_at: number;
  share_id: any; // Can be more specific if known
  archived: boolean;
  pinned: boolean;
  meta: FolderMeta;
  folder_id: string;
  currentResponseIds: string[];
  currentId: string;
  chat_type: string;
  models: string[]; // Assuming string array based on usage
}

export interface ChatType {
  history: History;
  models: string[];
  messages: Message[]; // This seems to be an array of messages, not a map
}

export interface History {
  messages: MessageMap; // This is a map of messages
  currentId: string;
  currentResponseIds: string[];
}

export interface MessageMap {
  [key: string]: Message; // Key is the message ID
}

export interface Message {
  id: string;
  role: string; // "user" | "model"
  content: string;
  models?: string[];
  chat_type: string;
  sub_chat_type: string;
  edited: boolean;
  error: any; // Can be more specific if known
  extra: MessageExtra;
  feature_config: FeatureConfig;
  parentId?: string;
  turn_id: any; // Can be more specific if known
  childrenIds: string[];
  files?: ChatFile[]; // Renamed from 'File' to avoid conflict
  timestamp: number;
  reasoning_content?: any; // Only present for model messages
  model?: string;
  modelName?: string;
  modelIdx?: number;
  content_list?: ContentList[]; // Only present for model messages
  is_stop?: boolean;
  meta?: MessageMeta; // This seems to be for model messages
  feedbackId?: any; // Can be more specific if known
  annotation?: any; // Can be more specific if known
  done?: boolean;
  info?: MessageInfo;
}

export interface MessageExtra {
  meta: SubChatTypeMeta;
  endTime?: number; // Only present for model messages
}

export interface SubChatTypeMeta {
  subChatType: string;
}

export interface FeatureConfig {
  thinking_enabled: boolean;
  output_schema: string;
  instructions: any; // Can be more specific if known
  research_mode: string;
  thinking_budget?: number;
}

export interface ChatFile { // Consolidated File interface
  id: string;
  name: string;
  file_type: string;
  type: string;
  file_class: string;
  size: number;
  url: string;
  file: StoredFileDetails;
  collection_name: string;
  progress: number;
  status: string;
  greenNet: string;
  error: string;
  itemId: string;
  showType: string;
  uploadTaskId: string;
}

export interface StoredFileDetails {
  created_at: number;
  data: {}; // Can be more specific if known
  filename: string;
  hash: any; // Can be more specific if known
  id: string;
  user_id: string;
  meta: StoredFileMeta;
  update_at: number;
}

export interface StoredFileMeta {
  name: string;
  size: number;
  content_type: string;
}

export interface ContentList {
  content: string;
  phase: string;
  status: string;
  extra: any; // Can be more specific if known
  role: string;
  usage: UsageStats;
}

export interface UsageStats {
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  output_tokens_details?: OutputTokensDetails;
}

export interface OutputTokensDetails {
  reasoning_tokens: number;
}

export interface MessageMeta {} // Empty interface, seems to be for model messages

export interface MessageInfo {
  suggest: string[];
}

export interface FolderMeta {
  timestamp: number;
  tags: string[];
}