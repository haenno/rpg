from django.db.models import deletion
from django.db.models.aggregates import Count
from django.shortcuts import render

# Create your views here.

from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import auth
from rjh_rpg.models import UserChar
from rjh_rpg.forms import UserCharForm
from rjh_rpg.models import GameState
from rjh_rpg.models import GameScenes
from rjh_rpg.models import LobbySlots

def signup(request):
    if request.user.is_authenticated:
        return render(request, 'msg_redirect.html', {
            'msg':'Du bist bereits angemeldet!', 
            'target':'/user_profile/'
            })
    else:
        if request.method == "POST":
            if request.POST['password1'] == request.POST['password2']:
                try:
                    User.objects.get(username = request.POST['username'])
                    return render (request,'signup.html', {'error':'Benutzername ist bereits vergeben!'})
                except User.DoesNotExist:
                    user = User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                    auth.login(request,user)
                    return render(request,'msg_redirect.html',{'msg':'Du wurdest erfolgreich angemeldet!','target':'/user_profile/'})
            else:
                return render (request,'signup.html', {'error':'Passwörter stimmen nicht überein!'})
        else:
            return render(request,'signup.html')

def login(request):
    if request.user.is_authenticated:
        return render(request,'msg_redirect.html',{'msg':'Du bist bereits angemeldet!','target':'/user_profile/'})
    else:
        if request.method == 'POST':
            user = auth.authenticate(username=request.POST['username'],password = request.POST['password'])
            if user is not None:
                auth.login(request,user)
                # (TODO!) should we delete gamesessions here?
                return redirect('home')
            else:
                return render (request,'login.html', {'error':'Benutzername oder Passwort falsch!'})
        else:
            return render(request,'login.html')

def logout(request):
    if request.user.is_authenticated:
        
        current_user_obj = User.objects.get(id=request.user.id)
        GameState_char_obj = GameState.objects.filter(char_user=current_user_obj)

        user_char_list = UserChar.objects.filter(usernickname=current_user_obj)
        for user_char in user_char_list:
            try:
                LobbySlots.objects.get(user_char_id=user_char).delete()
            except:
                pass
        try:
            GameState.objects.get(char_user=current_user_obj).delete()
        except:
            pass
        

        auth.logout(request)

        return render(request,'msg_redirect.html',{'msg':'Du wurdest ausgelogt!'})
    else:
        return render(request,'msg_redirect.html',{'msg':'Du bist nicht angemeldet!','target':'/login/'})
        


def home(request):
    if request.user.is_authenticated:
        pass
    else:
        pass
    return render(request, 'home.html')


def user_profile(request):
    if request.user.is_authenticated:
        return render(request, 'user_profile.html')
    else:
        return render(request,'msg_redirect.html',{'msg':'Du bist nicht angemeldet!','target':'/login/'})


# game views and logic:

def chars(request):
    if request.user.is_authenticated:
        current_user_obj = User.objects.get(id=request.user.id)
        GameState_char_obj = GameState.objects.filter(char_user=current_user_obj)
        
        # (TODO!) Only delete here, if the game found, is over. 
        # show a link to the game, if it is not yet finished.

        try:
            GameState.objects.get(char_user=current_user_obj).delete()
        except:
            pass

        char_list = UserChar.objects.filter(usernickname=request.user).order_by('name')
        
        current_user = User.objects.get(id=request.user.id)
        active_char = GameState.objects.filter(char_user=current_user)

        form = UserCharForm()
        
        if request.method == 'POST':
            form = UserCharForm(request.POST)
            if form.is_valid():
                tmp_form = form.save(commit=False)
                tmp_form.usernickname = request.user
                tmp_form.save()
                return render(request,'msg_redirect.html',{'msg':'Der Char wurde erfolgreich angelegt!','target':'/chars/'})
            else:
                pass
        
        return render(request, 'chars.html', {'chars': char_list, 'form': form, 'active_char' : active_char})

    else:
        return render(request,'msg_redirect.html',{'msg':'Du bist nicht angemeldet!','target':'/login/'})
 
    
def worldmap(request): # (TODO!) dringend zusammenkopierten kram aufräumen und zusammenpacken
    if request.user.is_authenticated:

        # (TODO!) redirect to maybe running game        

        # set char to worldmap after selection in /chars/
        if request.method == 'POST':
            # set UserChar to worldmap 
            char_to_gamestate = GameState()

            char_id = request.POST.get('char')

            char_from_db = UserChar.objects.get(id=char_id)
            char_to_gamestate.char = char_from_db

            current_user = User.objects.get(id=request.user.id)
            char_to_gamestate.char_user = current_user

            try: # check if user has an active char allready, if yes redirect
                try_active_user = GameState.objects.get(char_user=current_user)
                print("try active user ging")
            except:
                print("try active user ging nicht!")

            # save GameState item on post data, also catch reload error with post data
            try:
                char_to_gamestate.save()
            except:
                return redirect('/worldmap/')
            
        # get user obj from logged in user
        current_user_obj = User.objects.get(id=request.user.id)

        # delete lobby slots
        user_char_list = UserChar.objects.filter(usernickname=current_user_obj)
        for user_char in user_char_list:
            try:
                LobbySlots.objects.get(user_char_id=user_char).delete()
                print("deleted user from lobbyslots")
            except:
                pass            

        # get gamestate obj based on the user object
        GameState_char_obj = GameState.objects.filter(char_user=current_user_obj)
        
        # try if char is selected, if not redirect to char selection
        try:
            char_id = GameState_char_obj[0].id
            print(char_id)
        except:
            return render(request,'msg_redirect.html',{'msg':'Du musst einen Char auswählen!','target':'/chars/'})

        # (TODO!) Only update here, if the game found, is over. 
        # show a link to the game, if it is not yet finished.


        # set char to worldmap (place = 0)
        # (TODO!) Only update if no unfinished game is running
        # if a game is running, show link...

        char_id_update = str(GameState_char_obj[0].char.id)
        update_test = GameState.objects.filter(char=char_id_update).update(place=0)
        print(update_test)

        # prepare nessesary lists for worldmap        
        active_char_list = GameState.objects.filter(place=0).order_by('char') # place 0 = worldmap
        game_scenes_list = GameScenes.objects.order_by('name') # place 0 = worldmap
        
        complete_game_scenes_list = []

        for scene in game_scenes_list: 

            players_in_chat = GameState.objects.filter(place=scene.id)

            players_in_chat_counter = 0
            for player_in_chat in players_in_chat:
                players_in_chat_counter = players_in_chat_counter + 1

            waiting_players = LobbySlots.objects.filter(game_scene_id=scene.id)

            player_counter = 0
            for waiting_player in waiting_players:
                player_counter = player_counter + 1
            
            complete_game_scenes_list.append({
                'name': scene.name,
                'req_players': scene.req_players,
                'waiting_players': player_counter,
                'players_in_chat_counter' : players_in_chat_counter,
                'id': scene.id,
                }
            )
            
        char_name = str(GameState_char_obj[0].char)
        char_user = str(GameState_char_obj[0].char_user)

        user_char_char_id = UserChar.objects.filter(name=char_name)
        
        char_id_form =  str(user_char_char_id[0].id)
        return render(request,
            'worldmap.html',
            {
                'char_id': char_id_form,
                'char_name' : char_name,
                'char_user' : char_user,
                'active_char_list' : active_char_list,
                'game_scenes_list': complete_game_scenes_list,

            }
        )

    else:
        return render(request,'msg_redirect.html',{'msg':'Du bist nicht angemeldet!','target':'/login/'})

# from YT Chat howto
#def room(request, room_name):
#    return render(request, 'chatroom.html', {
#        'room_name': room_name
#    })

def scene(request):
    if not request.user.is_authenticated:
        return render(request,'msg_redirect.html',{'msg':'Du bist nicht angemeldet!','target':'/login/'})    
    if not request.method == 'POST':
        return render(request,'msg_redirect.html',{'msg':'Du musst eine Szene auswählen!','target':'/chars/'})

    return render(request,'msg_redirect.html',{'msg':'(TODO!) SZENE ERREICHT! Gamelogik...','target':'/chars/'})
    # add logic for games...
    pass

    
def lobby_jumper(request):
    if not request.user.is_authenticated:
        return render(request,'msg_redirect.html',{'msg':'Du bist nicht angemeldet!','target':'/login/'})    
    
    if request.method == 'POST':
        scene_id = request.POST.get('scene_id')

        if scene_id is None: 
            return render(request,'msg_redirect.html',{'msg':'Du musst eine Szene auswählen!','target':'/worldmap/'})    
        else:
            return redirect('/lobby-'+scene_id+'/')
    else:
        return render(request,'msg_redirect.html',{'msg':'Du musst eine Szene auswählen!','target':'/worldmap/'})    


def lobby(request, scene_id):
    if not request.user.is_authenticated:
        return render(request,'msg_redirect.html',{'msg':'Du bist nicht angemeldet!','target':'/login/'})    

    if not GameScenes.objects.filter(id=scene_id).exists():
        return render(request,'msg_redirect.html',{'msg':'Du musst eine existierende Szene auswählen!','target':'/worldmap/'})
    
    current_user_obj = User.objects.get(id=request.user.id)
    GameState_char_obj = GameState.objects.filter(char_user=current_user_obj)
    char_id = str(GameState_char_obj[0].char.id)

    # set char to the scene
    # (TODO!) Only update if no unfinished game is running
    # if a game is running, show link...

    GameState.objects.filter(char=char_id).update(place=scene_id)

    usr_obj = UserChar.objects.get(id=char_id)

    char_name = str(usr_obj)

    return render(request, 'lobby.html', {
            'char_id': char_id,
            'scene_id': scene_id,
            'char_name': char_name,
        }
    )
