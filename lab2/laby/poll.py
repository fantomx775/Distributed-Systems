from fastapi import FastAPI, HTTPException, Body, status
from pydantic import BaseModel
from typing import List

app = FastAPI()
class Vote(BaseModel):
    id: int
    vote: int
class Poll(BaseModel):
    id: int
    votes: List[Vote]

def generate_id():
    return len(polls) + 1

polls: List[Poll] = []

@app.post("/poll/", response_model=int, status_code=status.HTTP_201_CREATED)
async def create_poll():
    poll = Poll(id=generate_id(), votes=[])
    polls.append(poll)
    return poll.id

@app.get("/poll/", response_model=List[Poll], status_code=status.HTTP_200_OK)
async def get_polls():
    return polls

@app.get("/poll/{id}", response_model=Poll, status_code=status.HTTP_200_OK)
async def get_poll(id: int):
    for poll in polls:
        if poll.id == id:
            return poll
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

@app.put("/poll/{id}", response_model=Poll, status_code=status.HTTP_200_OK)
async def update_poll(id: int, votes: List[Vote] = Body(...)):
    for poll in polls:
        if poll.id == id:
            poll.votes = votes
            return poll
    poll = Poll(id=generate_id(), votes=votes)
    polls.append(poll)
    return poll.id

@app.delete("/poll/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_poll(id: int):
    for poll in polls:
        if poll.id == id:
            polls.remove(poll)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

@app.get("/poll/{id}/vote", response_model=List[Vote], status_code=status.HTTP_200_OK)
async def get_votes(id: int):
    for poll in polls:
        if poll.id == id:
            return len(poll.votes)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

@app.post("/poll/{id}/vote", response_model=int, status_code=status.HTTP_201_CREATED)
async def vote(id: int, vote: int = Body(...)):
    for poll in polls:
        if poll.id == id:
            poll.votes.append(vote)
            return len(poll.votes)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

@app.get("/poll/{id}/vote/{vote_id}", response_model=Vote, status_code=status.HTTP_200_OK)
async def get_vote(id: int, vote_id: int):
    for poll in polls:
        if poll.id == id:
            for vote in poll.votes:
                if vote.id == vote_id:
                    return vote
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote not found")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

@app.put("/poll/{id}/vote/{vote_id}", response_model=Vote, status_code=status.HTTP_200_OK)
async def update_vote(id: int, vote_id: int, vote: int = Body(...)):
    for poll in polls:
        if poll.id == id:
            poll.votes[vote_id] = vote
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")

@app.delete("/poll/{id}/vote/{vote_id}", response_model=int, status_code=status.HTTP_204_NO_CONTENT)
async def delete_vote(id: int, vote_id: int):
    for poll in polls:
        if poll.id == id:
            poll.votes.remove(vote_id)
            return vote_id
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poll not found")