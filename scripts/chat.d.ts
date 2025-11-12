export type AllChatArray = ChatFolder[]

// Canonical names for improved clarity (backwards-compatible aliases)
// Prefer these in new code. Existing exported interfaces remain unchanged below.
export type ChatFolderList = ChatFolder[]
export type Chat = ChatType
export type ChatHistory = History
export type MessageMap = Record<string, Message>

// Consolidated/common shapes (aliasing the most general variants)
export type FeatureConfigCommon = FeatureConfig21
export type ExtraEnvelope = Extra21
export type MetaWithSubChatType = Meta35
export type EmptyMeta = Meta37

export type AttachmentFile = File9
export type StoredFile = File10
export type FileMeta = Meta36
export type BlobData = Data5

export type UsageStats = Usage11
export type OutputTokensDetailsCommon = OutputTokensDetails8

export interface ChatFolder {
  id: string
  user_id: string
  title: string
  chat: ChatType
  updated_at: number
  created_at: number
  share_id: any
  archived: boolean
  pinned: boolean
  meta: Meta38
  folder_id: string
  currentResponseIds: string[]
  currentId: string
  chat_type: string
  models: any
}

export interface ChatType {
  history: History
  models: string[]
  messages: Message[]
}

export interface History {
  messages: Messages
  currentId: string
  currentResponseIds: string[]
}

export interface Messages {
  "5d24ecfd-151e-4f8b-985e-2f7a652e2f78": N5d24ecfd151e4f8b985e2f7a652e2f78
  "a4db66c9-7716-4b82-aa1f-3597071d9dda": A4db66c977164b82Aa1f3597071d9dda
  "81787889-1829-4d3f-9e15-969732bd45d1": N8178788918294d3f9e15969732bd45d1
  "20192877-1f6b-4754-95a0-d777a53be3f4": N201928771f6b475495a0D777a53be3f4
  "4034769e-eb7e-4ced-8cf6-87d66d74c9a5": N4034769eEb7e4ced8cf687d66d74c9a5
  "e3f0028f-4def-4c10-ac98-e261571ccb4f": E3f0028f4def4c10Ac98E261571ccb4f
  "96ddb9da-b30d-43b2-938f-e8434b7ce56a": N96ddb9daB30d43b2938fE8434b7ce56a
  "ba0316db-4b49-4535-b042-6a41782a81d0": Ba0316db4b494535B0426a41782a81d0
  "5e133866-a0e6-4974-a7f9-2db2f76b2d72": N5e133866A0e64974A7f92db2f76b2d72
  "00a711bc-5de6-48e8-929d-46ffed80a8e5": N00a711bc5de648e8929d46ffed80a8e5
  "d43ce6ed-77a8-4d7c-87c5-dd49a67b9562": D43ce6ed77a84d7c87c5Dd49a67b9562
  "2013557b-9a96-49a5-9596-c5f5d7568e1c": N2013557b9a9649a59596C5f5d7568e1c
  "418791c8-43b7-4c80-8bfa-bbda0f243f6a": N418791c843b74c808bfaBbda0f243f6a
  "f45ef030-c572-4c1b-a79c-6b754ae53938": F45ef030C5724c1bA79c6b754ae53938
  "040b8d6f-2e7f-430d-bda3-80678c18a269": N040b8d6f2e7f430dBda380678c18a269
  "ba0808e3-f0f3-446b-a660-edfa276f3547": Ba0808e3F0f3446bA660Edfa276f3547
  "7a435f4b-4859-4a88-a820-aa089d5b7495": N7a435f4b48594a88A820Aa089d5b7495
  "1bcf8b38-6d97-4364-92dc-417692212383": N1bcf8b386d97436492dc417692212383
  "e15d565f-39e0-458f-b001-1c7f36f6fe2d": E15d565f39e0458fB0011c7f36f6fe2d
  "371e8637-4119-427f-9673-4753bcfbf9c5": N371e86374119427f96734753bcfbf9c5
}

export interface N5d24ecfd151e4f8b985e2f7a652e2f78 {
  id: string
  role: string
  content: string
  models: string[]
  chat_type: string
  sub_chat_type: string
  edited: boolean
  error: any
  extra: Extra
  feature_config: FeatureConfig
  parentId: any
  turn_id: any
  childrenIds: string[]
  files: File[]
  timestamp: number
}

export interface Extra {
  meta: Meta
}

export interface Meta {
  subChatType: string
}

export interface FeatureConfig {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
}

export interface File {
  id: string
  name: string
  file_type: string
  type: string
  file_class: string
  size: number
  url: string
  file: File2
  collection_name: string
  progress: number
  status: string
  greenNet: string
  error: string
  itemId: string
  showType: string
  uploadTaskId: string
}

export interface File2 {
  created_at: number
  data: Data
  filename: string
  hash: any
  id: string
  user_id: string
  meta: Meta2
  update_at: number
}

export interface Data {}

export interface Meta2 {
  name: string
  size: number
  content_type: string
}

export interface A4db66c977164b82Aa1f3597071d9dda {
  role: string
  content: string
  reasoning_content: any
  chat_type: string
  sub_chat_type: string
  model: string
  modelName: string
  modelIdx: number
  id: string
  parentId: string
  childrenIds: string[]
  feature_config: FeatureConfig2
  content_list: ContentList[]
  is_stop: boolean
  edited: boolean
  error: any
  meta: Meta3
  extra: Extra2
  feedbackId: any
  turn_id: any
  annotation: any
  done: boolean
  info: any
  timestamp: number
}

export interface FeatureConfig2 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
}

export interface ContentList {
  content: string
  phase: string
  status: string
  extra: any
  role: string
  usage: Usage
}

export interface Usage {
  input_tokens: number
  output_tokens: number
  total_tokens: number
}

export interface Meta3 {}

export interface Extra2 {
  meta: Meta4
  endTime: number
}

export interface Meta4 {
  subChatType: string
}

export interface N8178788918294d3f9e15969732bd45d1 {
  id: string
  role: string
  content: string
  models: string[]
  chat_type: string
  sub_chat_type: string
  edited: boolean
  error: any
  extra: Extra3
  feature_config: FeatureConfig3
  parentId: string
  turn_id: any
  childrenIds: string[]
  files: File3[]
  timestamp: number
}

export interface Extra3 {
  meta: Meta5
}

export interface Meta5 {
  subChatType: string
}

export interface FeatureConfig3 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
}

export interface File3 {
  id: string
  name: string
  file_type: string
  type: string
  file_class: string
  size: number
  url: string
  file: File4
  collection_name: string
  progress: number
  status: string
  greenNet: string
  error: string
  itemId: string
  showType: string
  uploadTaskId: string
}

export interface File4 {
  created_at: number
  data: Data2
  filename: string
  hash: any
  id: string
  user_id: string
  meta: Meta6
  update_at: number
}

export interface Data2 {}

export interface Meta6 {
  name: string
  size: number
  content_type: string
}

export interface N201928771f6b475495a0D777a53be3f4 {
  role: string
  content: string
  reasoning_content: any
  chat_type: string
  sub_chat_type: string
  model: string
  modelName: string
  modelIdx: number
  id: string
  parentId: string
  childrenIds: string[]
  feature_config: FeatureConfig4
  content_list: ContentList2[]
  is_stop: boolean
  edited: boolean
  error: any
  meta: Meta7
  extra: Extra4
  feedbackId: any
  turn_id: any
  annotation: any
  done: boolean
  info: any
  timestamp: number
}

export interface FeatureConfig4 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
}

export interface ContentList2 {
  content: string
  phase: string
  status: string
  extra: any
  role: string
  usage: Usage2
}

export interface Usage2 {
  input_tokens: number
  output_tokens: number
  total_tokens: number
}

export interface Meta7 {}

export interface Extra4 {
  meta: Meta8
  endTime: number
}

export interface Meta8 {
  subChatType: string
}

export interface N4034769eEb7e4ced8cf687d66d74c9a5 {
  id: string
  role: string
  content: string
  models: string[]
  chat_type: string
  sub_chat_type: string
  edited: boolean
  error: any
  extra: Extra5
  feature_config: FeatureConfig5
  parentId: string
  turn_id: any
  childrenIds: string[]
  files: File5[]
  timestamp: number
}

export interface Extra5 {
  meta: Meta9
}

export interface Meta9 {
  subChatType: string
}

export interface FeatureConfig5 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget: number
}

export interface File5 {
  id: string
  name: string
  file_type: string
  type: string
  file_class: string
  size: number
  url: string
  file: File6
  collection_name: string
  progress: number
  status: string
  greenNet: string
  error: string
  itemId: string
  showType: string
  uploadTaskId: string
}

export interface File6 {
  created_at: number
  data: Data3
  filename: string
  hash: any
  id: string
  user_id: string
  meta: Meta10
  update_at: number
}

export interface Data3 {}

export interface Meta10 {
  name: string
  size: number
  content_type: string
}

export interface E3f0028f4def4c10Ac98E261571ccb4f {
  role: string
  content: string
  reasoning_content: any
  chat_type: string
  sub_chat_type: string
  model: string
  modelName: string
  modelIdx: number
  id: string
  parentId: string
  childrenIds: string[]
  feature_config: FeatureConfig6
  content_list: ContentList3[]
  is_stop: boolean
  edited: boolean
  error: any
  meta: Meta11
  extra: Extra6
  feedbackId: any
  turn_id: any
  annotation: any
  done: boolean
  info: Info
  timestamp: number
}

export interface FeatureConfig6 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget: number
}

export interface ContentList3 {
  content: string
  phase: string
  status: string
  extra: any
  role: string
  usage: Usage3
}

export interface Usage3 {
  input_tokens: number
  output_tokens: number
  total_tokens: number
  output_tokens_details: OutputTokensDetails
}

export interface OutputTokensDetails {
  reasoning_tokens: number
}

export interface Meta11 {}

export interface Extra6 {
  meta: Meta12
  endTime: number
}

export interface Meta12 {
  subChatType: string
}

export interface Info {
  suggest: string[]
}

export interface N96ddb9daB30d43b2938fE8434b7ce56a {
  id: string
  role: string
  content: string
  models: string[]
  chat_type: string
  sub_chat_type: string
  edited: boolean
  error: any
  extra: Extra7
  feature_config: FeatureConfig7
  parentId: string
  turn_id: any
  childrenIds: string[]
  files: any[]
  timestamp: number
}

export interface Extra7 {
  meta: Meta13
}

export interface Meta13 {
  subChatType: string
}

export interface FeatureConfig7 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget: number
}

export interface Ba0316db4b494535B0426a41782a81d0 {
  role: string
  content: string
  reasoning_content: any
  chat_type: string
  sub_chat_type: string
  model: string
  modelName: string
  modelIdx: number
  id: string
  parentId: string
  childrenIds: string[]
  feature_config: FeatureConfig8
  content_list: ContentList4[]
  is_stop: boolean
  edited: boolean
  error: any
  meta: Meta14
  extra: Extra8
  feedbackId: any
  turn_id: any
  annotation: any
  done: boolean
  info: Info2
  timestamp: number
}

export interface FeatureConfig8 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget: number
}

export interface ContentList4 {
  content: string
  phase: string
  status: string
  extra: any
  role: string
  usage: Usage4
}

export interface Usage4 {
  input_tokens: number
  output_tokens: number
  total_tokens: number
  output_tokens_details: OutputTokensDetails2
}

export interface OutputTokensDetails2 {
  reasoning_tokens: number
}

export interface Meta14 {}

export interface Extra8 {
  meta: Meta15
  endTime: number
}

export interface Meta15 {
  subChatType: string
}

export interface Info2 {
  suggest: string[]
}

export interface N5e133866A0e64974A7f92db2f76b2d72 {
  id: string
  role: string
  content: string
  models: string[]
  chat_type: string
  sub_chat_type: string
  edited: boolean
  error: any
  extra: Extra9
  feature_config: FeatureConfig9
  parentId: string
  turn_id: any
  childrenIds: string[]
  files: any[]
  timestamp: number
}

export interface Extra9 {
  meta: Meta16
}

export interface Meta16 {
  subChatType: string
}

export interface FeatureConfig9 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget: number
}

export interface N00a711bc5de648e8929d46ffed80a8e5 {
  role: string
  content: string
  reasoning_content: any
  chat_type: string
  sub_chat_type: string
  model: string
  modelName: string
  modelIdx: number
  id: string
  parentId: string
  childrenIds: string[]
  feature_config: FeatureConfig10
  content_list: ContentList5[]
  is_stop: boolean
  edited: boolean
  error: any
  meta: Meta17
  extra: Extra10
  feedbackId: any
  turn_id: any
  annotation: any
  done: boolean
  info: Info3
  timestamp: number
}

export interface FeatureConfig10 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget: number
}

export interface ContentList5 {
  content: string
  phase: string
  status: string
  extra: any
  role: string
  usage: Usage5
}

export interface Usage5 {
  input_tokens: number
  output_tokens: number
  total_tokens: number
  output_tokens_details: OutputTokensDetails3
}

export interface OutputTokensDetails3 {
  reasoning_tokens: number
}

export interface Meta17 {}

export interface Extra10 {
  meta: Meta18
  endTime: number
}

export interface Meta18 {
  subChatType: string
}

export interface Info3 {
  suggest: string[]
}

export interface D43ce6ed77a84d7c87c5Dd49a67b9562 {
  id: string
  role: string
  content: string
  models: string[]
  chat_type: string
  sub_chat_type: string
  edited: boolean
  error: any
  extra: Extra11
  feature_config: FeatureConfig11
  parentId: string
  turn_id: any
  childrenIds: string[]
  files: any[]
  timestamp: number
}

export interface Extra11 {
  meta: Meta19
}

export interface Meta19 {
  subChatType: string
}

export interface FeatureConfig11 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget: number
}

export interface N2013557b9a9649a59596C5f5d7568e1c {
  role: string
  content: string
  reasoning_content: any
  chat_type: string
  sub_chat_type: string
  model: string
  modelName: string
  modelIdx: number
  id: string
  parentId: string
  childrenIds: string[]
  feature_config: FeatureConfig12
  content_list: ContentList6[]
  is_stop: boolean
  edited: boolean
  error: any
  meta: Meta20
  extra: Extra12
  feedbackId: any
  turn_id: any
  annotation: any
  done: boolean
  info: Info4
  timestamp: number
}

export interface FeatureConfig12 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget: number
}

export interface ContentList6 {
  content: string
  phase: string
  status: string
  extra: any
  role: string
  usage: Usage6
}

export interface Usage6 {
  input_tokens: number
  output_tokens: number
  total_tokens: number
  output_tokens_details: OutputTokensDetails4
}

export interface OutputTokensDetails4 {
  reasoning_tokens: number
}

export interface Meta20 {}

export interface Extra12 {
  meta: Meta21
  endTime: number
}

export interface Meta21 {
  subChatType: string
}

export interface Info4 {
  suggest: string[]
}

export interface N418791c843b74c808bfaBbda0f243f6a {
  id: string
  role: string
  content: string
  models: string[]
  chat_type: string
  sub_chat_type: string
  edited: boolean
  error: any
  extra: Extra13
  feature_config: FeatureConfig13
  parentId: string
  turn_id: any
  childrenIds: string[]
  files: any[]
  timestamp: number
}

export interface Extra13 {
  meta: Meta22
}

export interface Meta22 {
  subChatType: string
}

export interface FeatureConfig13 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
}

export interface F45ef030C5724c1bA79c6b754ae53938 {
  role: string
  content: string
  reasoning_content: any
  chat_type: string
  sub_chat_type: string
  model: string
  modelName: string
  modelIdx: number
  id: string
  parentId: string
  childrenIds: string[]
  feature_config: FeatureConfig14
  content_list: ContentList7[]
  is_stop: boolean
  edited: boolean
  error: any
  meta: Meta23
  extra: Extra14
  feedbackId: any
  turn_id: any
  annotation: any
  done: boolean
  info: any
  timestamp: number
}

export interface FeatureConfig14 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
}

export interface ContentList7 {
  content: string
  phase: string
  status: string
  extra: any
  role: string
  usage: Usage7
}

export interface Usage7 {
  input_tokens: number
  output_tokens: number
  total_tokens: number
}

export interface Meta23 {}

export interface Extra14 {
  meta: Meta24
  endTime: number
}

export interface Meta24 {
  subChatType: string
}

export interface N040b8d6f2e7f430dBda380678c18a269 {
  id: string
  role: string
  content: string
  models: string[]
  chat_type: string
  sub_chat_type: string
  edited: boolean
  error: any
  extra: Extra15
  feature_config: FeatureConfig15
  parentId: string
  turn_id: any
  childrenIds: string[]
  files: File7[]
  timestamp: number
}

export interface Extra15 {
  meta: Meta25
}

export interface Meta25 {
  subChatType: string
}

export interface FeatureConfig15 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget: number
}

export interface File7 {
  id: string
  name: string
  file_type: string
  type: string
  file_class: string
  size: number
  url: string
  file: File8
  collection_name: string
  progress: number
  status: string
  greenNet: string
  error: string
  itemId: string
  showType: string
  uploadTaskId: string
}

export interface File8 {
  created_at: number
  data: Data4
  filename: string
  hash: any
  id: string
  user_id: string
  meta: Meta26
  update_at: number
}

export interface Data4 {}

export interface Meta26 {
  name: string
  size: number
  content_type: string
}

export interface Ba0808e3F0f3446bA660Edfa276f3547 {
  role: string
  content: string
  reasoning_content: any
  chat_type: string
  sub_chat_type: string
  model: string
  modelName: string
  modelIdx: number
  id: string
  parentId: string
  childrenIds: string[]
  feature_config: FeatureConfig16
  content_list: ContentList8[]
  is_stop: boolean
  edited: boolean
  error: any
  meta: Meta27
  extra: Extra16
  feedbackId: any
  turn_id: any
  annotation: any
  done: boolean
  info: Info5
  timestamp: number
}

export interface FeatureConfig16 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget: number
}

export interface ContentList8 {
  content: string
  phase: string
  status: string
  extra: any
  role: string
  usage: Usage8
}

export interface Usage8 {
  input_tokens: number
  output_tokens: number
  total_tokens: number
  output_tokens_details: OutputTokensDetails5
}

export interface OutputTokensDetails5 {
  reasoning_tokens: number
}

export interface Meta27 {}

export interface Extra16 {
  meta: Meta28
  endTime: number
}

export interface Meta28 {
  subChatType: string
}

export interface Info5 {
  suggest: string[]
}

export interface N7a435f4b48594a88A820Aa089d5b7495 {
  id: string
  role: string
  content: string
  models: string[]
  chat_type: string
  sub_chat_type: string
  edited: boolean
  error: any
  extra: Extra17
  feature_config: FeatureConfig17
  parentId: string
  turn_id: any
  childrenIds: string[]
  files: any[]
  timestamp: number
}

export interface Extra17 {
  meta: Meta29
}

export interface Meta29 {
  subChatType: string
}

export interface FeatureConfig17 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget: number
}

export interface N1bcf8b386d97436492dc417692212383 {
  role: string
  content: string
  reasoning_content: any
  chat_type: string
  sub_chat_type: string
  model: string
  modelName: string
  modelIdx: number
  id: string
  parentId: string
  childrenIds: string[]
  feature_config: FeatureConfig18
  content_list: ContentList9[]
  is_stop: boolean
  edited: boolean
  error: any
  meta: Meta30
  extra: Extra18
  feedbackId: any
  turn_id: any
  annotation: any
  done: boolean
  info: Info6
  timestamp: number
}

export interface FeatureConfig18 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget: number
}

export interface ContentList9 {
  content: string
  phase: string
  status: string
  extra: any
  role: string
  usage: Usage9
}

export interface Usage9 {
  input_tokens: number
  output_tokens: number
  total_tokens: number
  output_tokens_details: OutputTokensDetails6
}

export interface OutputTokensDetails6 {
  reasoning_tokens: number
}

export interface Meta30 {}

export interface Extra18 {
  meta: Meta31
  endTime: number
}

export interface Meta31 {
  subChatType: string
}

export interface Info6 {
  suggest: string[]
}

export interface E15d565f39e0458fB0011c7f36f6fe2d {
  id: string
  role: string
  content: string
  models: string[]
  chat_type: string
  sub_chat_type: string
  edited: boolean
  error: any
  extra: Extra19
  feature_config: FeatureConfig19
  parentId: string
  turn_id: any
  childrenIds: string[]
  files: any[]
  timestamp: number
}

export interface Extra19 {
  meta: Meta32
}

export interface Meta32 {
  subChatType: string
}

export interface FeatureConfig19 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget: number
}

export interface N371e86374119427f96734753bcfbf9c5 {
  role: string
  content: string
  reasoning_content: any
  chat_type: string
  sub_chat_type: string
  model: string
  modelName: string
  modelIdx: number
  id: string
  parentId: string
  childrenIds: any[]
  feature_config: FeatureConfig20
  content_list: ContentList10[]
  is_stop: boolean
  edited: boolean
  error: any
  meta: Meta33
  extra: Extra20
  feedbackId: any
  turn_id: any
  annotation: any
  done: boolean
  info: any
  timestamp: number
}

export interface FeatureConfig20 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget: number
}

export interface ContentList10 {
  content: string
  phase: string
  status: string
  extra: any
  role: string
  usage: Usage10
}

export interface Usage10 {
  input_tokens: number
  output_tokens: number
  total_tokens: number
  output_tokens_details: OutputTokensDetails7
}

export interface OutputTokensDetails7 {
  reasoning_tokens: number
}

export interface Meta33 {}

export interface Extra20 {
  meta: Meta34
  endTime: number
}

export interface Meta34 {
  subChatType: string
}

export interface Message {
  id: string
  role: string
  content: string
  models?: string[]
  chat_type: string
  sub_chat_type: string
  edited: boolean
  error: any
  extra: Extra21
  feature_config: FeatureConfig21
  parentId?: string
  turn_id: any
  childrenIds: string[]
  files?: File9[]
  timestamp: number
  reasoning_content: any
  model?: string
  modelName?: string
  modelIdx?: number
  content_list?: ContentList11[]
  is_stop?: boolean
  meta?: Meta37
  feedbackId: any
  annotation: any
  done?: boolean
  info?: Info7
}

export interface Extra21 {
  meta: Meta35
  endTime?: number
}

export interface Meta35 {
  subChatType: string
}

export interface FeatureConfig21 {
  thinking_enabled: boolean
  output_schema: string
  instructions: any
  research_mode: string
  thinking_budget?: number
}

export interface File9 {
  id: string
  name: string
  file_type: string
  type: string
  file_class: string
  size: number
  url: string
  file: File10
  collection_name: string
  progress: number
  status: string
  greenNet: string
  error: string
  itemId: string
  showType: string
  uploadTaskId: string
}

export interface File10 {
  created_at: number
  data: Data5
  filename: string
  hash: any
  id: string
  user_id: string
  meta: Meta36
  update_at: number
}

export interface Data5 {}

export interface Meta36 {
  name: string
  size: number
  content_type: string
}

export interface ContentList11 {
  content: string
  phase: string
  status: string
  extra: any
  role: string
  usage: Usage11
}

export interface Usage11 {
  input_tokens: number
  output_tokens: number
  total_tokens: number
  output_tokens_details?: OutputTokensDetails8
}

export interface OutputTokensDetails8 {
  reasoning_tokens: number
}

export interface Meta37 {}

export interface Info7 {
  suggest: string[]
}

export interface Meta38 {
  timestamp: number
  tags: string[]
}

