% NSX2Mat_fromDI.m  (sibling of NSX2Mat_formatted.m)
% For patients whose "raw" upload is already an openNSx export saved as a MATLAB .mat
% (NSX struct; DI's 202604/202605 uploads) rather than a Blackrock .ns6 that openNSx can read.
% Writes the same per-channel BL<chanID>.mat files (data in uV) so neur1_preproc / sorting.m run unchanged.

% CHANGES WITH PATIENT
subj = '202605';
rawDir = sprintf('../../data/%s/raw/', subj);
d = dir(fullfile(rawDir, '*_ns6.mat'));
assert(numel(d) == 1, 'Expected exactly one *_ns6.mat in %s', rawDir);
rawMat = fullfile(rawDir, d(1).name);

% create dir if it doesnt exist
outDir = fullfile('..','..','data', subj, 'osort_mat', 'nsx2mat');
if ~exist(outDir, 'dir')
    mkdir(outDir);
end
prefix = 'BL';

% 1) Load the export; NSX.Data is nChan x T int16 in digital units, one row per enabled channel
S = load(rawMat, 'NSX'); NS6 = S.NSX; clear S;
chanIDs  = NS6.MetaTags.ChannelID(:)';   % e.g., [193 194 ...]
nEnabled = numel(chanIDs); % no. of channels
assert(size(NS6.Data, 1) == nEnabled, 'Data rows (%d) != ChannelID count (%d)', size(NS6.Data, 1), nEnabled);
fprintf('%s: %d channels, %.1f min\n', d(1).name, nEnabled, NS6.MetaTags.DataDurationSec / 60);

% 2) Loop over ChannelIDs; digital -> uV exactly as openNSx 'uV' does (x MaxAnalog/MaxDigi = 0.25 uV/bit)
for ii = 1:nEnabled
    thisID  = chanIDs(ii);                   % original Blackrock ChannelID
    idx     = ii;                            % index in the enabled list (1..nEnabled)

    uVperBit = double(NS6.ElectrodesInfo(idx).MaxAnalogValue) / double(NS6.ElectrodesInfo(idx).MaxDigiValue);
    data = double(NS6.Data(idx, :)) * uVperBit;   % 1 x T row vector

    MetaTags = NS6.MetaTags;
    MetaTags.ChannelID = thisID;

    ElectrodesInfo = struct( ...
    'Type', 'CC', ...
    'ChannelID', thisID, ...
    'Label', sprintf('chan%d', thisID), ...
    'MaxDigiValue', int16(32764), ...
    'MinDigiValue', int16(-32764), ...
    'MaxAnalogValue', int16(8191), ...
    'MinAnalogValue', int16(-8191), ...
    'AnalogUnits', 'uV' ...
    );

    RawData = data;
    scalingFactor = 1;

    outFile = fullfile(outDir, sprintf('%s%d.mat', prefix, thisID));
    save(outFile,'data','RawData','MetaTags','ElectrodesInfo','scalingFactor','-v7.3');

    fprintf('Saved %s (ChannelID %d)\n', outFile, thisID);
end
