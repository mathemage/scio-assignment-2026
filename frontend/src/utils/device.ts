// Generate or retrieve a unique device ID
export const getDeviceId = (): string => {
  const STORAGE_KEY = 'device_id';
  
  // Check if device ID already exists in localStorage
  let deviceId = localStorage.getItem(STORAGE_KEY);
  
  if (!deviceId) {
    // Generate a new device ID
    deviceId = `device_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
    localStorage.setItem(STORAGE_KEY, deviceId);
  }
  
  return deviceId;
};

// Check if a device has already joined a specific group
export const hasJoinedGroup = (groupId: number): boolean => {
  const STORAGE_KEY = `joined_group_${groupId}`;
  return localStorage.getItem(STORAGE_KEY) === 'true';
};

// Mark that a device has joined a group
export const markGroupJoined = (groupId: number): void => {
  const STORAGE_KEY = `joined_group_${groupId}`;
  localStorage.setItem(STORAGE_KEY, 'true');
};
