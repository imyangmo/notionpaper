import { atom } from 'nanostores';

export const getTitle = atom("");
export const getPostList = atom([])
export const getDesc = atom("")
export const getTopics = atom([])

export function setTitle(name){
    getTitle.set(name)
}

export function setDesc(name){
    getDesc.set(name)
}

export function setPostList(list){
    getPostList.set(list)
}

export function setTopics(topics){
    getTopics.set(topics)
}