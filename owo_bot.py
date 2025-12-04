# owo_bot.py
# Requisiti: discord.py 2.x
# pip install -U discord.py
# Bot Token: MTQ0NjE4ODQ4NTU4NDM1NTMzMA.GDkkJr.26ydz21-U5qVbvUoVI2nTXtJQE4rl5L-Vk0Txg
# Guild ID: 1445463044305059843

import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
import asyncio
from typing import Dict, List, Optional

# ===========================
# CONFIG - SOSTITUISCI GLI ID QUI
# ===========================
GUILD_ID = 1445463044305059843  # <- sostituisci con l'ID del server (int)
BOT_TOKEN = "MTQ0NjE4ODQ4NTU4NDM1NTMzMA.GDkkJr.26ydz21-U5qVbvUoVI2nTXtJQE4rl5L-Vk0Txg"   # <- sostituisci con token bot

# Ruoli OWO: preferibile inserire gli ID (int). Se None, il bot userà il "name" per trovare/creare.
ROLE_IDS = {
    "silenced": 1445536877330301232,
    "Root Access": 1445525563119898808,
    "Council-Core": 1445525734926848153,
    "SuperUser": 1445536051270647920,
    "sys-bot": 1445536717665865728,
    "OPERATIVES_SEPARATOR": 1445537575837110282,  # il separator (non operativo)
    "Kernel-Operative": 1445536236919066675,
    "Senior-Node": 1445536337653534821,
    "Node-Operative": 1445536426656530432,
    "Field-Agent": 1445536562288005322,
    "Initiate": 1445536627169693840,
    "CyberNet": 1445537305698894016,
    "Verified": 1445541728147734553,
}

# Canali OWO: inserisci ID dei canali
CHANNEL_IDS = {
    # Public entry
    "tickets": 1445666033170911362,
    "verify": 1445540415468998676,
    "apply": 1445544904418791514,

    # CORE-NET
    "sys-announcements": 1445520436795277483,
    "user-handshake": 1445520776773242880,
    "support-desk": 1445520828975284345,
    "firewall-foes": 1446018718634344504,

    # OPS-NET
    "main-terminal": 1445520524837912628,
    "tactics-node": 1445520962169606236,
    "media": 1445762278170427423,
    "capture-logs": 1445520998429491320,
    "resource-vault": 1445521028590735553,
    "logs-archive": 1446260116868562994,
    
    # ECON-NET
    "quota-directives": 1445521136249995406,
    "quota-reports": 1445521163361980457,
    "fund-ledger": 1445521212800372797,

    # SYS-TOOLS
    "bot-shell": 1445521400080105584,
    "web-status": 1445521423937437782,
    "log-channel": 1446260693614460968,

    # VOICE
    "ops-channel": 1445521515402494025,
    "lounge": 1445521598927868046,
    "afk": 1445521735024771082,

    # COUNCIL
    "applications-review": 1445546159446953984,
    "council-chat": 1445555090470469722,
    "ticket-logs": 1445555246125551746,
    "council-lounge": 1445555198897688720,

}

# ===========================
# RUOLI (DEFINIZIONE DI DEFAULT) - i colori si usano solo se si crea il ruolo
# NOTA: se passi gli ID, le proprietà qui servono come "reference" (nome/perm)
# ===========================
ROLE_CONFIG_ORDER = [
    {"name": "silenced", "color": 0x6B6B6B, "perms": discord.Permissions.none()},
    {"name": "Root Access", "color": 0x2AA2FF, "perms": discord.Permissions(administrator=True)},
    {"name": "Council-Core", "color": 0x1BC7C7, "perms": discord.Permissions(manage_messages=True, mute_members=True, deafen_members=True, move_members=True, kick_members=True, manage_channels=True, view_channel=True, send_messages=True, manage_roles=True)},
    {"name": "SuperUser", "color": 0x3FA8FF, "perms": discord.Permissions(view_channel=True, send_messages=True, attach_files=True, embed_links=True, read_message_history=True, connect=True, speak=True, manage_messages=True)},
    {"name": "sys-bot", "color": 0x9E9E9E, "perms": discord.Permissions(administrator=True)},
    {"name": "|| OPERATIVES ||", "color": 0x1BC7C7, "perms": discord.Permissions.none()},  # separator
    {"name": "Kernel-Operative", "color": 0x32E0FF, "perms": discord.Permissions(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True)},
    {"name": "Senior-Node", "color": 0x6AD5FF, "perms": discord.Permissions(view_channel=True, send_messages=True)},
    {"name": "Node-Operative", "color": 0x8FDFFF, "perms": discord.Permissions(view_channel=True, send_messages=True)},
    {"name": "Field-Agent", "color": 0xB0ECFF, "perms": discord.Permissions(view_channel=True, send_messages=True)},
    {"name": "Initiate", "color": 0xD6F8FF, "perms": discord.Permissions(view_channel=True, read_message_history=True)},
    {"name": "CyberNet", "color": 0x00AEEF, "perms": discord.Permissions(view_channel=True)},
    {"name": "Verified", "color": 0x5865F2, "perms": discord.Permissions.none()},
]

# Channel => mapping di allow/deny (role names)
CHANNEL_OVERRIDES_DEF = {
    # public onboarding
    "tickets": {"allow": ["Initiate", "Verified", "CyberNet"], "deny": ["silenced"]},
    "verify": {"allow": ["Initiate", "Verified", "CyberNet"], "deny": ["silenced"]},
    "apply": {"allow": ["Initiate", "Verified", "CyberNet"], "deny": ["silenced"]},

    # CORE-NET
    "sys-announcements": {"allow": ["Initiate","CyberNet","Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"], "deny":["silenced"]},
    "user-handshake": {"allow": ["Initiate","CyberNet","Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"], "deny":["silenced"]},
    "support-desk": {"allow": ["Initiate","CyberNet","Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"], "deny":["silenced"]},
    "firewall-foes": {"allow": ["Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"], 
                      "deny":["Initiate","Verified","silenced"]},

    # OPS-NET
    "main-terminal": {"allow": ["Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"],
                      "deny":["Initiate","Verified","silenced"]},

    "tactics-node": {"allow": ["Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"],
                     "deny":["Initiate","Verified","silenced"]},

    "capture-logs": {"allow": ["Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"],
                     "deny":["Initiate","Verified","silenced"]},

    "media": {"allow": ["Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"],
              "deny":["Initiate","Verified","silenced"]},

    "resource-vault": {"allow": ["Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"],
                       "deny":["Initiate","Verified","silenced"]},
    
    "logs-archive": {"allow": ["Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"],
                     "deny":["Initiate","Verified","silenced"]},


    # ECON-NET
    "quota-directives": {"allow": ["Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"],
                         "deny":["Initiate","Verified","silenced"]},
    "quota-reports": {"allow": ["Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"],
                      "deny":["Initiate","Verified","silenced"]},
    "fund-ledger": {"allow": ["Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"],
                    "deny":["Initiate","Verified","silenced"]},

    # SYS-TOOLS (restricted)
    "bot-shell": {"allow": ["SuperUser","Council-Core","Root Access","sys-bot"],
                  "deny":["Initiate","Verified","Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","silenced","CyberNet"]},

    "web-status": {"allow": ["SuperUser","Council-Core","Root Access","sys-bot"],
                   "deny":["Initiate","Verified","Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","silenced","CyberNet"]},

    "log-channel": {"allow": ["sys-bot","Root Access","Council-Core"],
                    "deny":["Initiate","Verified","CyberNet","Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","silenced"]},

    # VOICE-OPS
    "ops-channel": {"allow": ["Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"],
                    "deny":["Initiate","Verified","silenced"]},

    "lounge": {"allow": ["Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"],
               "deny":["Initiate","Verified","silenced"]},

    "afk": {"allow": ["Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","Council-Core","Root Access"],
            "deny":["Initiate","Verified","silenced"]},

    # COUNCIL - only Council-Core + Root
    "applications-review": {"allow": ["Council-Core","Root Access"],
                            "deny":["Initiate","Verified","Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","silenced","CyberNet"]},

    "council-chat": {"allow": ["Council-Core","Root Access"],
                     "deny":["Initiate","Verified","Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","silenced","CyberNet"]},

    "ticket-logs": {"allow": ["Council-Core","Root Access"],
                    "deny":["Initiate","Verified","Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","silenced","CyberNet"]},

    "council-lounge": {"allow": ["Council-Core","Root Access"],
                       "deny":["Initiate","Verified","Kernel-Operative","Senior-Node","Node-Operative","Field-Agent","SuperUser","silenced","CyberNet"]},
}

# ===========================
# Utility / Persistence
# ===========================
DATA_FILE = "owo_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"quotas": {}, "applications": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===========================
# Bot setup
# ===========================
intents = discord.Intents.none()
intents.guilds = True
intents.members = True   # necessario per gestire ruoli e membri
intents.messages = True
intents.message_content = True  # necessario se leggi contenuti dei messaggi
intents.voice_states = True     # se gestisci canali vocali
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ===========================
# Helpers
# ===========================
async def fetch_role(guild: discord.Guild, name: str, role_id: Optional[int], perms: discord.Permissions, color_int: int) -> discord.Role:
    """Recupera o crea un ruolo. Se role_id fornito, usa quello; altrimenti cerca per name e crea se manca."""
    if role_id:
        role = guild.get_role(role_id)
        if role:
            # aggiorna perm/color se necessario
            try:
                await role.edit(permissions=perms, colour=discord.Colour(color_int))
            except Exception:
                pass
            return role
    # cerca per nome
    role = discord.utils.get(guild.roles, name=name)
    if role:
        try:
            await role.edit(permissions=perms, colour=discord.Colour(color_int))
        except Exception:
            pass
        return role
    # crea
    role = await guild.create_role(name=name, permissions=perms, colour=discord.Colour(color_int))
    return role

def make_overwrite_for_channel(is_voice: bool, allow: bool) -> discord.PermissionOverwrite:
    """
    Crea un PermissionOverwrite e imposta i permessi principali che vogliamo gestire.
    Non tocca permessi non elencati (lascia None).
    """
    if is_voice:
        return discord.PermissionOverwrite(view_channel=allow, connect=allow, speak=allow)
    else:
        return discord.PermissionOverwrite(view_channel=allow, send_messages=allow, read_message_history=True, attach_files=allow, embed_links=allow)

async def set_channel_permissions_non_destructive(channel: discord.abc.GuildChannel, role: discord.Role, overwrite: discord.PermissionOverwrite):
    """
    Applica i permessi ruolo per ruolo (non sovrascrive gli altri).
    """
    await channel.set_permissions(role, overwrite=overwrite)

def role_name_from_cfg_entry(entry):
    return entry["name"]

def desired_role_order_objects(guild: discord.Guild, created_roles_map: Dict[str, discord.Role]) -> List[discord.Role]:
    """
    Restituisce la lista dei role objects nell'ordine esatto di ROLE_CONFIG_ORDER,
    dal più alto al più basso (pronto per edit_role_positions).
    """
    roles = []
    for cfg in ROLE_CONFIG_ORDER:
        rname = cfg["name"]
        role = created_roles_map.get(rname)
        if role:
            roles.append(role)
    return roles

# ===========================
# Commands & Core
# ===========================
@bot.event
async def on_ready():
    print(f"Bot online as {bot.user} (id={bot.user.id})")
    try:
        await tree.sync(guild=discord.Object(id=GUILD_ID))
        print("Slash commands sincronizzati per il guild.")
    except Exception as e:
        print("Errore sincronizzazione:", e)

@tree.command(name="check_hierarchy", description="Controlla quali ruoli il bot può gestire", guild=discord.Object(id=GUILD_ID))
async def check_hierarchy(interaction: discord.Interaction):
    guild = interaction.guild
    me = guild.get_member(bot.user.id)
    bot_top_pos = me.top_role.position
    report_lines = []
    for cfg in ROLE_CONFIG_ORDER:
        rname = cfg["name"]
        # cerca ruolo nel guild
        role = discord.utils.get(guild.roles, name=rname)
        if role:
            can_manage = bot_top_pos > role.position and me.guild_permissions.manage_roles
            report_lines.append(f"- {rname}: posizione {role.position} — {'OK' if can_manage else 'NO (bot troppo basso o perm mancanti)'}")
        else:
            report_lines.append(f"- {rname}: NON TROVATO")
    # anche check generico per ruolo bot
    bot_role = me.top_role
    report = f"Bot top-role: `{bot_role.name}` (pos {bot_role.position})\n\n" + "\n".join(report_lines)
    await interaction.response.send_message(f"```{report}```", ephemeral=True)

@tree.command(name="sync_full", description="Sincronizza ruoli, gerarchia, canali, override e basic systems", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(administrator=True)
async def sync_full(interaction: discord.Interaction):
    """Esegue la sincronizzazione completa: crea/aggiorna ruoli, ordina, setta permessi canali, init quota/data."""
    await interaction.response.send_message("🔄 Avviando sync completo. Controlli preliminari...", ephemeral=True)
    guild = interaction.guild
    me = guild.get_member(bot.user.id)
    if not me.guild_permissions.administrator:
        await interaction.followup.send("❌ Il bot non ha permessi administrator. Assegna admin o assicurati che il bot abbia i permessi necessari.", ephemeral=True)
        return

    data = load_data()

    # 1) CREAZIONE / RECUPERO RUOLI
    created_roles = {}
    for cfg in ROLE_CONFIG_ORDER:
        name = cfg["name"]
        role_id = ROLE_IDS.get(name) or ROLE_IDS.get(name.replace(" ", "-")) or None
        role = await fetch_role(guild, name, role_id, cfg["perms"], cfg["color"])
        created_roles[name] = role

    # 2) POSIZIONAMENTO (ordinamento esatto - l'elemento 0 deve essere il più alto)
    ordered_roles = desired_role_order_objects(guild, created_roles)
    # edit_role_positions wants a mapping role->position int; higher number = higher in list.
    positions = {}
    top_base = len(ordered_roles) + 10  # lascia margine
    bot_member = guild.get_member(bot.user.id)

    for i, role in enumerate(ordered_roles):
        # controlla che il ruolo sia sotto il top role del bot
        if role.position < bot_member.top_role.position:
            positions[role] = top_base - i

    if positions:
        try:
            await guild.edit_role_positions(positions=positions)
        except Exception as e:
            await interaction.followup.send(f"⚠️ Errore quando si aggiornano le posizioni dei ruoli: {e}", ephemeral=True)

    # 3) SET CANALI PER ROLE (non-distruttivo)
    for cname, definition in CHANNEL_OVERRIDES_DEF.items():
        chan_id = CHANNEL_IDS.get(cname)
        if chan_id:
            channel = guild.get_channel(chan_id)
        else:
            # fallback by name
            channel = discord.utils.get(guild.channels, name=cname)
        if not channel:
            # canale non esistente -> skip
            continue

        # allow
        for role_name in definition.get("allow", []):
            role_obj = created_roles.get(role_name) or discord.utils.get(guild.roles, name=role_name)
            if not role_obj:
                continue
            overwrite = make_overwrite_for_channel(isinstance(channel, discord.VoiceChannel), True)
            await set_channel_permissions_non_destructive(channel, role_obj, overwrite)

        # deny
        for role_name in definition.get("deny", []):
            role_obj = created_roles.get(role_name) or discord.utils.get(guild.roles, name=role_name)
            if not role_obj:
                continue
            overwrite = make_overwrite_for_channel(isinstance(channel, discord.VoiceChannel), False)
            await set_channel_permissions_non_destructive(channel, role_obj, overwrite)

    # 4) sys-bot & bot role position check
    me = guild.get_member(bot.user.id)
    if me.top_role.position < min([r.position for r in ordered_roles if r is not None]):
        await interaction.followup.send("⚠️ Avviso: il ruolo del bot è *sotto* alcuni ruoli OWO. Sposta il ruolo del BOT sopra tutti i ruoli OWO prima di eseguire operazioni di gestione completa.", ephemeral=True)
    else:
        await interaction.followup.send("✅ Sincronizzazione ruoli e override completata. Controlla i canali e le posizioni ruoli.", ephemeral=True)

    # 5) inizializza storage (se necessario)
    if "quotas" not in data:
        data["quotas"] = {}
    if "applications" not in data:
        data["applications"] = {}
    save_data(data)

    # log
    log_ch = CHANNEL_IDS.get("log-channel")
    if log_ch:
        ch = guild.get_channel(log_ch)
        if ch:
            await ch.send("✅ /sync_full eseguito con successo.")

@tree.command(name="roleinfo", description="Mostra informazioni su un ruolo OWO", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(role_name="Nome del ruolo (esatto)")
async def roleinfo(interaction: discord.Interaction, role_name: str):
    guild = interaction.guild
    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        await interaction.response.send_message("Ruolo non trovato.", ephemeral=True)
        return
    info = (
        f"Nome: {role.name}\n"
        f"ID: {role.id}\n"
        f"Posizione: {role.position}\n"
        f"Menzionabile: {role.mentionable}\n"
        f"Permissions: {role.permissions.value}\n"
    )
    await interaction.response.send_message(f"```{info}```", ephemeral=True)

# ---------------------------
# STAFF UTILITY (promote/demote/silence)
# ---------------------------

@tree.command(name="silence", description="Assegna silenced ad un utente (mute testuale)", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(manage_roles=True)
async def silence(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    guild = interaction.guild
    sil = discord.utils.get(guild.roles, name="silenced")
    if not sil:
        await interaction.response.send_message("Ruolo silenced non trovato.", ephemeral=True)
        return
    await member.add_roles(sil, reason=reason or f"silenced by {interaction.user}")
    await interaction.response.send_message(f"{member.mention} silenziato.", ephemeral=True)

@tree.command(name="unsilence", description="Rimuove silenced da un utente", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(manage_roles=True)
async def unsilence(interaction: discord.Interaction, member: discord.Member):
    guild = interaction.guild
    sil = discord.utils.get(guild.roles, name="silenced")
    if not sil:
        await interaction.response.send_message("Ruolo silenced non trovato.", ephemeral=True)
        return
    await member.remove_roles(sil, reason=f"unsilenced by {interaction.user}")
    await interaction.response.send_message(f"{member.mention} non è più silenziato.", ephemeral=True)

@tree.command(name="promote", description="Promuove un membro al ruolo operativo successivo", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(manage_roles=True)
async def promote(interaction: discord.Interaction, member: discord.Member):
    """
    Logica semplice: prende la lista gerarchica OPERATIVES e promuove al ruolo successivo.
    """
    guild = interaction.guild
    operative_order = ["Initiate", "Field-Agent", "Node-Operative", "Senior-Node", "Kernel-Operative"]
    current = None
    for r in operative_order[::-1]:
        role = discord.utils.get(guild.roles, name=r)
        if role in member.roles:
            current = r
            break
    if current is None:
        # se non ha alcuno, assegna Initiate
        r = discord.utils.get(guild.roles, name="Initiate")
        if r:
            await member.add_roles(r, reason=f"Promoted to Initiate by {interaction.user}")
            await interaction.response.send_message(f"{member.mention} assegnato a Initiate.", ephemeral=True)
        else:
            await interaction.response.send_message("Ruolo Initiate non trovato.", ephemeral=True)
        return
    idx = operative_order.index(current)
    if idx == len(operative_order)-1:
        await interaction.response.send_message(f"{member.mention} è già al massimo ruolo operativo ({current}).", ephemeral=True)
        return
    next_role = discord.utils.get(guild.roles, name=operative_order[idx+1])
    cur_role_obj = discord.utils.get(guild.roles, name=current)
    if next_role:
        await member.add_roles(next_role, reason=f"Promoted by {interaction.user}")
        if cur_role_obj:
            await member.remove_roles(cur_role_obj, reason=f"Promoted by {interaction.user}")
        await interaction.response.send_message(f"{member.mention} promosso a {next_role.name}.", ephemeral=True)
    else:
        await interaction.response.send_message("Ruolo destinazione non trovato.", ephemeral=True)

@tree.command(name="demote", description="Degrada un membro al ruolo operativo precedente", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(manage_roles=True)
async def demote(interaction: discord.Interaction, member: discord.Member):
    guild = interaction.guild
    operative_order = ["Initiate", "Field-Agent", "Node-Operative", "Senior-Node", "Kernel-Operative"]
    current = None
    for r in operative_order[::-1]:
        role = discord.utils.get(guild.roles, name=r)
        if role in member.roles:
            current = r
            break
    if not current:
        await interaction.response.send_message("Il membro non ha ruoli operativi OWO.", ephemeral=True)
        return
    idx = operative_order.index(current)
    if idx == 0:
        await interaction.response.send_message(f"{member.mention} è già al ruolo più basso ({current}).", ephemeral=True)
        return
    prev_role = discord.utils.get(guild.roles, name=operative_order[idx-1])
    cur_role_obj = discord.utils.get(guild.roles, name=current)
    if prev_role:
        await member.add_roles(prev_role, reason=f"Demoted by {interaction.user}")
        if cur_role_obj:
            await member.remove_roles(cur_role_obj, reason=f"Demoted by {interaction.user}")
        await interaction.response.send_message(f"{member.mention} degradato a {prev_role.name}.", ephemeral=True)
    else:
        await interaction.response.send_message("Ruolo precedente non trovato.", ephemeral=True)

@bot.tree.command(name="approve_application", description="Approva la candidatura di un utente e assegna il ruolo Initiate", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="L'utente da approvare")
@app_commands.checks.has_permissions(administrator=True)
async def approve_application(interaction: discord.Interaction, user: discord.Member):
    guild = interaction.guild
    role_initiate = discord.utils.get(guild.roles, name="Initiate")
    if not role_initiate:
        await interaction.response.send_message("❌ Ruolo 'Initiate' non trovato. Esegui /sync_full prima.", ephemeral=True)
        return

    if role_initiate in user.roles:
        await interaction.response.send_message(f"⚠️ {user.mention} ha già il ruolo Initiate.", ephemeral=True)
        return

    try:
        await user.add_roles(role_initiate, reason=f"Application approved by {interaction.user}")
        await interaction.response.send_message(f"✅ {user.mention} è stato approvato e ha ricevuto il ruolo Initiate.", ephemeral=True)

        # LOG in log-channel
        log_ch_id = CHANNEL_IDS.get("log-channel")
        if log_ch_id:
            log_ch = guild.get_channel(log_ch_id)
            if log_ch:
                await log_ch.send(f"✅ {user.mention} approvato da {interaction.user} e ruolo Initiate assegnato.")
        
        # Aggiornamento storage (facoltativo)
        data = load_data()
        if "applications" not in data:
            data["applications"] = {}
        data["applications"][str(user.id)] = {"status": "approved", "approved_by": str(interaction.user)}
        save_data(data)

    except Exception as e:
        await interaction.response.send_message(f"❌ Errore durante l'assegnazione del ruolo: {e}", ephemeral=True)

# ===========================
# Event logging (semplice)
# ===========================
@bot.event
async def on_member_join(member):
    guild = member.guild
    ch_id = CHANNEL_IDS.get("log-channel")
    if ch_id:
        ch = guild.get_channel(ch_id)
        if ch:
            await ch.send(f"🚪 {member} è entrato nel server.")

@bot.event
async def on_member_remove(member):
    guild = member.guild
    ch_id = CHANNEL_IDS.get("log-channel")
    if ch_id:
        ch = guild.get_channel(ch_id)
        if ch:
            await ch.send(f"❌ {member} ha lasciato il server.")

# ===========================
# Avvio
# ===========================
if __name__ == "__main__":
    bot.run(BOT_TOKEN)
