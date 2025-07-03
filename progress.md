# Progress Checkpoint  
**Last Updated:** July 3, 2025  

This document outlines the current development status of the application, including implemented features, architectural notes, and known issues. Below is a video walkthrough of the application in action:

#### Video Walkthrough

<div>
    <a href="https://www.loom.com/share/1e78b83eb7b643ebad175aea476781fe">
    </a>
    <a href="https://www.loom.com/share/1e78b83eb7b643ebad175aea476781fe">
      <img style="max-width:300px;" src="https://cdn.loom.com/sessions/thumbnails/1e78b83eb7b643ebad175aea476781fe-32e42ccb79945803-full-play.gif">
    </a>
</div>

#### Authentication  
- Google Sign-In via Firebase successfully integrated  
- ID token securely sent to backend for verification  
- First-time login triggers automatic user registration  
- Domain restriction enabled (toggleable feature)


#### User Profile  
- User data retrieved from `/users/me` endpoint  
- Editable fields: name, bio, and age  
- Profile photo upload supported via Cloudinary  
- Location auto-detection with option for manual input  
- Photo gallery support in progress (CRUD for up to 3 images pending)


#### Feed  
- Static/dummy posts shown in an infinite scroll format  
- Posts include author info, timestamp, and text content  
- Feed UI integrates seamlessly with sidebar and top navigation bar  

#### App Architecture  
- Protected routes implemented using `<PrivateRoute />`  
- Responsive sidebar and top navigation bar  
- AuthContext handles persistent login using localStorage  
- Firebase credentials and backend secrets securely separated  
- Modular folder structure optimized for scalability and maintenance  

#### Known Bugs & TODOs  
- [ ] Token auto-refresh not implemented (expires after 1 hour). **Clear browser application storage (localStorage)** before restarting the app to avoid stale tokens or profile conflicts  
- [ ] Layout breaks on smaller screens – needs responsive tweaks  
